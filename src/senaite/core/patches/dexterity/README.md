# Dexterity Patches

This package contains patches for Dexterity based content types.

## Dexterity Content

The module `dexterity_content` contains patches for the class `plone.dexterity.content.DexterityContent`,
which is the base class for our `Item` and `Container` based contents.

### Patches

The following methods are patched:

- `getLabels`
- `isTemporary`

### Reason

Provide a similar methods for DX contents as for AT contents.

**getLabels**: Get SENAITE labels (dynamically extended fields)

**isTemporary**: Checks if an object contains a temporary ID to avoid further indexing/processing
