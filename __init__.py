from .nodes import ArtistListIterator, ArtistPromptComposer, SaveImageWithArtistTag

NODE_CLASS_MAPPINGS = {
    "ArtistListIterator": ArtistListIterator,
    "ArtistPromptComposer": ArtistPromptComposer,
    "SaveImageWithArtistTag": SaveImageWithArtistTag
}

# 这里的名字决定了你在 ComfyUI 右键菜单里看到什么
# 我稍微改了一下，让它看起来更符合 V2.0 的功能
NODE_DISPLAY_NAME_MAPPINGS = {
    "ArtistListIterator": "👉 1. Artist Iterator (V2)", 
    "ArtistPromptComposer": "👉 2. Artist Prompt Station (Template)",
    "SaveImageWithArtistTag": "💾 3. Save Image (Smart Name)"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']