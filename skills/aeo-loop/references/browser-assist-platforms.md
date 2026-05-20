# Browser-assist platforms

Reference for `browser_assist.py` — supported platforms, URL construction, clipboard fallback.

---

## How browser-assist works

1. Skill calls `browser_assist.<platform>(url, draft_text)`.
2. The function validates the URL scheme (http/https/mailto only — javascript: and data: are rejected).
3. Where the platform accepts pre-filled content via URL params, the draft is URL-encoded into the query string and the browser opens to the pre-filled form.
4. Where pre-fill is not possible (platform requires JS to populate the form), the draft is copied to the clipboard and the browser opens to a blank form. The operator pastes manually.
5. The skill never submits. The operator reviews the pre-filled or pasted content and clicks Submit themselves.

---

## Supported platforms

### Generic form (`generic_form`)
- **Pre-fill method:** URL param `?body=` or `?content=` depending on the form
- **Fallback:** clipboard copy if the target URL has no known param
- **Usage:** catch-all for any URL not matched by a named platform

### Quora India (`quora_india`)
- **URL pattern:** `https://www.quora.com/answer/<question-slug>`
- **Pre-fill method:** clipboard (Quora's answer editor is JS-rendered; URL params don't reach the editor)
- **Operator flow:** browser opens to the Quora answer page → operator pastes from clipboard → reviews → Submit

### JustDial (`justdial`)
- **URL pattern:** listing management URL supplied by the operator
- **Pre-fill method:** clipboard
- **Operator flow:** browser opens to listing edit page → operator pastes → reviews → Submit

### IndiaMART (`indiamart`)
- **URL pattern:** product/listing edit URL supplied by the operator
- **Pre-fill method:** clipboard
- **Operator flow:** browser opens to IndiaMART dashboard → operator pastes → reviews → Submit

### MouthShut (`mouthshut`)
- **URL pattern:** `https://www.mouthshut.com/write-review/<product-slug>`
- **Pre-fill method:** clipboard
- **Operator flow:** browser opens to review form → operator pastes → reviews → Submit

---

## Clipboard fallback behaviour

When a platform does not support URL pre-fill:

1. `pyperclip.copy(draft_text)` is called to write the draft to the system clipboard.
2. If `pyperclip` is unavailable, the draft is printed to stdout with a `--- COPY THIS ---` header so the operator can copy manually.
3. The browser opens immediately after the clipboard write.
4. The skill prints: `Draft copied to clipboard. Paste into the form and click Submit.`

---

## Adding a new platform

Add a function to `browser_assist.py`:

```python
def new_platform(listing_url: str, draft: str) -> None:
    _validate_scheme(listing_url)          # always call this first
    pyperclip.copy(draft)                  # or build a pre-fill URL
    webbrowser.open(listing_url)
    print("Draft copied to clipboard. Paste into the form and click Submit.")
```

Register it in the `_BUILDERS` dict (same file) so the `build()` dispatcher can find it. `SUPPORTED_PLATFORMS` is derived from `_BUILDERS` automatically — no separate update needed.

---

## URL scheme allowlist

Only `http://`, `https://`, and `mailto:` are permitted. Any other scheme raises `ValueError` before the browser is opened. This prevents `javascript:` and `data:` URI injection.
