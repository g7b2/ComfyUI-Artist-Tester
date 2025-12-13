import random
import re
from nodes import SaveImage

# --------------------------------------------------------------------------------
# Node 1: Artist List Iterator (With Reset, Auto Increment & Anti-Cache)
# --------------------------------------------------------------------------------
class ArtistListIterator:
    """
    Iterates through a list of strings (artists/prompts).
    Features:
    - Internal counter for infinite batch looping.
    - Reset capability to restart from the beginning.
    - IS_CHANGED checks to ensure ComfyUI re-executes the node every time.
    """
    _internal_counter = 0

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text_list": ("STRING", {
                    "multiline": True, 
                    "default": "Greg Rutkowski\nartist:wlop\nartist:ciloranko",
                    "placeholder": "Enter one artist/tag per line..."
                }),
                "select_mode": (["Auto Increment", "Random", "Fixed (Use Input)"], {"default": "Auto Increment"}),
                "reset_counter": ("BOOLEAN", {"default": False, "label_on": "Reset to 0 (Run Once)", "label_off": "Continue Counting"}),
            },
            "optional": {
                "index_input": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("artist_tag",)
    FUNCTION = "get_item"
    CATEGORY = "🎨 Artist Tester"

    @classmethod
    def IS_CHANGED(s, **kwargs):
        # Always return NaN to force re-execution
        return float("NaN")

    def get_item(self, text_list, select_mode, reset_counter, index_input=0):
        # 1. Reset Logic
        if reset_counter:
            ArtistListIterator._internal_counter = 0
        
        # 2. Clean List
        items = [line.strip() for line in text_list.splitlines() if line.strip()]
        if not items:
            return ("",)

        # 3. Selection Logic
        current_idx = 0
        
        if select_mode == "Random":
            current_idx = random.randint(0, len(items) - 1)
        elif select_mode == "Auto Increment":
            current_idx = ArtistListIterator._internal_counter
            # Increment for the next run
            ArtistListIterator._internal_counter += 1
        else:
            # Fixed Mode
            current_idx = index_input if index_input is not None else 0

        # 4. Retrieval
        real_index = current_idx % len(items)
        selected_item = items[real_index]
        
        print(f"🎨 [Artist Tester] Batch {current_idx} | Mode: {select_mode} | Selected: {selected_item}")
        return (selected_item,)


# --------------------------------------------------------------------------------
# Node 2: Artist Prompt Composer (Outputs Text for Filename)
# --------------------------------------------------------------------------------
class ArtistPromptComposer:
    """
    Combines Base Prompt + Artist Tag + Negative Prompt.
    Outputs:
    - Positive Conditioning
    - Negative Conditioning
    - Final String (useful for saving filenames)
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "clip": ("CLIP", ),
                "positive_base": ("STRING", {
                    "multiline": True, 
                    "default": "masterpiece, best quality, 1girl, solo, portrait", 
                }),
                "negative_prompt": ("STRING", {
                    "multiline": True, 
                    "default": "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry", 
                }),
                "artist_tag": ("STRING", {"default": "", "forceInput": True}),
            }
        }

    RETURN_TYPES = ("CONDITIONING", "CONDITIONING", "STRING")
    RETURN_NAMES = ("positive", "negative", "final_text")
    FUNCTION = "encode"
    CATEGORY = "🎨 Artist Tester"

    def encode(self, clip, positive_base, negative_prompt, artist_tag):
        # Combine
        combined_text = f"{positive_base}, {artist_tag}"
        
        # Encode Positive
        tokens_pos = clip.tokenize(combined_text)
        cond_pos, pooled_pos = clip.encode_from_tokens(tokens_pos, return_pooled=True)
        
        # Encode Negative
        tokens_neg = clip.tokenize(negative_prompt)
        cond_neg, pooled_neg = clip.encode_from_tokens(tokens_neg, return_pooled=True)
        
        return ([[cond_pos, {"pooled_output": pooled_pos}]], [[cond_neg, {"pooled_output": pooled_neg}]], combined_text)


# --------------------------------------------------------------------------------
# Node 3: Save Image with Artist Tag (Fixes Windows Filename Errors)
# --------------------------------------------------------------------------------
class SaveImageWithArtistTag(SaveImage):
    """
    A specific SaveImage node that sanitizes filenames to prevent errors.
    Automatically converts 'artist:name' to 'artist-name' and removes illegal characters.
    """
    def __init__(self):
        super().__init__()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", ),
                # Force input allows connecting the string from Node 2 directly
                "filename_prefix": ("STRING", {"default": "ComfyUI", "forceInput": True}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "🎨 Artist Tester"

    def save_images(self, images, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        # --- Filename Sanitization Logic ---
        
        # 1. Replace colons (common in danbooru tags) with dashes
        # e.g., "artist:wlop" -> "artist-wlop"
        clean_prefix = filename_prefix.replace(":", "-")
        
        # 2. Remove other illegal Windows characters: \ / * ? " < > | and newlines
        clean_prefix = re.sub(r'[\\/*?"<>|\n\r]', "", clean_prefix)
        
        # 3. Truncate to avoid path length limit (max 150 chars for safety)
        if len(clean_prefix) > 150:
            clean_prefix = clean_prefix[:150] + "..."
            
        # 4. Ensure it's not empty
        clean_prefix = clean_prefix.strip()
        if not clean_prefix:
            clean_prefix = "Artist_Test"
            
        # --- End Logic ---

        return super().save_images(images, clean_prefix, prompt, extra_pnginfo)