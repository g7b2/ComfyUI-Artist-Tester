from .nodes import ArtistListIterator, ArtistPromptComposer, SaveImageWithArtistTag

NODE_CLASS_MAPPINGS = {
    "ArtistListIterator": ArtistListIterator,
    "ArtistPromptComposer": ArtistPromptComposer,
    "SaveImageWithArtistTag": SaveImageWithArtistTag
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ArtistListIterator": "👉 1. Artist Iterator (Auto)",
    "ArtistPromptComposer": "👉 2. Artist Prompt Station",
    "SaveImageWithArtistTag": "💾 3. Save Image (Auto Name)"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']