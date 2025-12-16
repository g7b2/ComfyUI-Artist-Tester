import random
import re
import hashlib
from nodes import SaveImage

# --------------------------------------------------------------------------------
# Node 1: Artist List Iterator V2 (Advanced Logic)
# --------------------------------------------------------------------------------
class ArtistListIterator:
    """
    V2 Features:
    - Random (No Repeat): Uses a seed to shuffle the list deterministically.
    - Isolated Counters: Different lists have separate counters (based on list hash).
    - Rich Outputs: Returns index, total count, and formatted index string.
    """
    # Dictionary to store counters for different lists
    # Key: MD5 hash of the text_list | Value: Current Counter
    _counters = {}

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
                "select_mode": (["Auto Increment", "Random (No Repeat)", "Random (Pure)", "Fixed (Use Input)"], {"default": "Auto Increment"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "reset_counter": ("BOOLEAN", {"default": False, "label_on": "Reset (Run Once)", "label_off": "Continue"}),
            },
            "optional": {
                "index_input": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "forceInput": True}),
            }
        }

    # Outputs: Tag, Current Index (Int), Total (Int), Index String (e.g. "001")
    RETURN_TYPES = ("STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("artist_tag", "current_index", "total_count", "index_string")
    FUNCTION = "get_item"
    CATEGORY = "🎨 Artist Tester"

    @classmethod
    def IS_CHANGED(s, **kwargs):
        return float("NaN")

    def get_item(self, text_list, select_mode, seed, reset_counter, index_input=0):
        # 1. Clean List
        items = [line.strip() for line in text_list.splitlines() if line.strip()]
        if not items:
            return ("", 0, 0, "0")
        
        total = len(items)

        # 2. Identify the list (Counter Isolation Logic)
        # We create a unique hash for this list content to isolate its counter
        list_hash = hashlib.md5(text_list.encode('utf-8')).hexdigest()

        # Initialize counter if not exists or reset requested
        if list_hash not in ArtistListIterator._counters or reset_counter:
            ArtistListIterator._counters[list_hash] = 0

        # 3. Determine Raw Counter
        internal_counter = ArtistListIterator._counters[list_hash]
        
        # 4. Mode Logic
        selected_index = 0
        
        if select_mode == "Fixed (Use Input)":
            selected_index = index_input if index_input is not None else 0
            
        elif select_mode == "Random (Pure)":
            # Pure random (legacy behavior, can repeat)
            selected_index = random.randint(0, total - 1)
            # We still increment counter to show progress
            ArtistListIterator._counters[list_hash] += 1
            
        elif select_mode == "Random (No Repeat)":
            # Shuffle Strategy:
            # Create a list of indices [0, 1, 2...]
            indices = list(range(total))
            # Shuffle them deterministically using the seed
            # This creates a "Playlist" that doesn't change order unless seed changes
            random.Random(seed).shuffle(indices)
            
            # Pick based on the counter loop
            loop_index = internal_counter % total
            selected_index = indices[loop_index]
            
            # Increment counter
            ArtistListIterator._counters[list_hash] += 1
            
        else: # Auto Increment
            selected_index = internal_counter % total
            ArtistListIterator._counters[list_hash] += 1

        # 5. Retrieve Item
        # Safe modulo just in case
        real_index = selected_index % total
        selected_item = items[real_index]
        
        # 6. Format Index String (e.g., 1 -> "001" if total is 100)
        # Calculate padding based on total digits
        padding = len(str(total))
        index_str = f"{real_index + 1:0{padding}d}"

        print(f"🎨 [Batch {internal_counter}] Mode: {select_mode} | Idx: {real_index+1}/{total} | {selected_item}")
        
        # Return: Tag, Index(0-based), Total, IndexStr(1-based)
        return (selected_item, real_index, total, index_str)


# --------------------------------------------------------------------------------
# Node 2: Artist Prompt Composer V2 (Flexible Template)
# --------------------------------------------------------------------------------
class ArtistPromptComposer:
    """
    V2 Features:
    - prompt_template: Allows custom positioning of the artist tag.
      Use {base} for the positive_base prompt.
      Use {artist} for the artist_tag.
      e.g., "{base}, style of {artist}" or "(artist:{artist}:1.2), {base}"
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
                "artist_tag": ("STRING", {"default": "", "forceInput": True}),
                # 🔥 New: Flexible Template
                "prompt_template": ("STRING", {
                    "multiline": False, 
                    "default": "{base}, {artist}", 
                    "placeholder": "Format: {base}, {artist}"
                }),
                "negative_prompt": ("STRING", {
                    "multiline": True, 
                    "default": "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry", 
                }),
            }
        }

    RETURN_TYPES = ("CONDITIONING", "CONDITIONING", "STRING")
    RETURN_NAMES = ("positive", "negative", "final_text")
    FUNCTION = "encode"
    CATEGORY = "🎨 Artist Tester"

    def encode(self, clip, positive_base, artist_tag, prompt_template, negative_prompt):
        # 1. Apply Template
        # If user cleared the template, fallback to default
        if not prompt_template.strip():
            prompt_template = "{base}, {artist}"
            
        combined_text = prompt_template.replace("{base}", positive_base).replace("{artist}", artist_tag)
        
        # 2. Encode Positive
        tokens_pos = clip.tokenize(combined_text)
        cond_pos, pooled_pos = clip.encode_from_tokens(tokens_pos, return_pooled=True)
        
        # 3. Encode Negative
        tokens_neg = clip.tokenize(negative_prompt)
        cond_neg, pooled_neg = clip.encode_from_tokens(tokens_neg, return_pooled=True)
        
        return ([[cond_pos, {"pooled_output": pooled_pos}]], [[cond_neg, {"pooled_output": pooled_neg}]], combined_text)


# --------------------------------------------------------------------------------
# Node 3: Save Image with Artist Tag (Sanitized) - Kept Same
# --------------------------------------------------------------------------------
class SaveImageWithArtistTag(SaveImage):
    def __init__(self):
        super().__init__()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", ),
                "filename_prefix": ("STRING", {"default": "ComfyUI", "forceInput": True}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "🎨 Artist Tester"

    def save_images(self, images, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        clean_prefix = filename_prefix.replace(":", "-")
        clean_prefix = re.sub(r'[\\/*?"<>|\n\r]', "", clean_prefix)
        if len(clean_prefix) > 150:
            clean_prefix = clean_prefix[:150] + "..."
        clean_prefix = clean_prefix.strip()
        if not clean_prefix:
            clean_prefix = "Artist_Test"
        return super().save_images(images, clean_prefix, prompt, extra_pnginfo)