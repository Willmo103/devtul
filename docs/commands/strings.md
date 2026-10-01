# Stream & String Processing (`dt str`, `dt ppdf`)

DevTul includes a dedicated suite of terminal stream and string inspection tools built on the `StringCommand` architecture. These tools allow you to inspect compiled binaries, extract text from PDFs, slice streams, and perform sed-like text substitutions natively across Windows, Linux, and macOS.

---

## 🔤 Printable String Extractor (`dt str` / `dt strings`)

The `dt str` command (available as `dt str`, `dt strings`, and standalone `dt-str`) extracts printable ASCII character sequences from compiled executables, DLLs, memory dumps, or raw data files.

### Syntax
```bash
dt str <PATH> [OPTIONS]
dt-str <PATH> [OPTIONS]
```

### Key Options
- `--min-len` / `-m`: Minimum sequence length to extract (default: `4`, matching standard GNU `strings`).
- Stream options: `--head`, `--tail`, `--grep`, `--sed`, `--numbered`, `--lines-with`.

### How It Works
`dt str` scans raw binary bytes in 1MB buffered chunks, identifying continuous byte sequences in the printable range (`0x20` to `0x7E` plus `\t`). It preserves strings spanning across buffer boundaries without loading huge files entirely into memory.

---

## 📄 Terminal PDF Inspector (`dt ppdf` / `dt print-pdf`)

The `dt ppdf` command (available as `dt ppdf`, `dt print-pdf`, and standalone `dt-ppdf`) extracts and filters text from PDF documents using [pdfplumber](https://github.com/jsvine/pdfplumber) directly inside your terminal.

### Syntax
```bash
dt ppdf <PATH> [OPTIONS]
dt-ppdf <PATH> [OPTIONS]
```

### Key Options
- `--pages` / `-p`: Page numbers or ranges to inspect (e.g. `'1-3'`, `'2,5'`, `'4'`).
- Stream options: `--head`, `--tail`, `--grep`, `--sed`, `--numbered`, `--lines-with`.

---

## 🌊 The `StringCommand` Stream Pipeline

Both `dt str` and `dt ppdf` (as well as future DevTul stream tools) pass extracted text through the standardized `StringCommand` processing pipeline.

```
Raw Text / Extracted Lines
  │
  ├── 1. Grep Filtering (--grep <regex>)
  │
  ├── 2. Term Filtering (--lines-with <term>)
  │
  ├── 3. Sed Pattern Substitution (--sed "s/pattern/replacement/flags")
  │
  ├── 4. Head Slicing (--head <N>)
  │
  ├── 5. Tail Slicing (--tail <N>)
  │
  └── 6. Line Numbering (--numbered)
        │
        └── Rich Console Output (with highlight for --lines-with)
```

### Sed Substitution Engine (`--sed`)
DevTul includes a native Python sed interpreter supporting:
- Standard slash syntax: `s/pattern/replacement/flags`
- Custom delimiters: `s#pattern#replacement#flags` or `s|pattern|replacement|flags` (useful when matching filepaths or URLs)
- Global flag (`g`): Replaces all occurrences in each line (omitting `g` replaces only the first occurrence).
- Case-insensitive flag (`i`): Matches pattern regardless of casing.

---

## 💡 Practical Examples

### Example 1: Extract URLs from an Executable
Scan a compiled binary for embedded web endpoints:
```powershell
dt str devtul.exe --grep "https://" --head 15
```

### Example 2: Inspect DLL Imports with Line Numbers
Search for kernel calls in a library:
```powershell
dt str kernel32.dll --min-len 8 --grep "CreateFile" --numbered
```

### Example 3: Highlight Matching Keywords with Rich Colors
Highlight all occurrences of `"password"` or `"secret"` with colored terminal banners:
```powershell
dt str config_dump.bin --lines-with "secret"
```

### Example 4: Filter Financial Figures in a PDF
Extract pages 1 through 3 and search for invoice totals:
```powershell
dt ppdf invoice.pdf --pages 1-3 --grep "Total" --numbered
```

### Example 5: Clean and Mask PDF Output with Sed
Substitute sensitive account numbers or terms on-the-fly:
```powershell
dt ppdf statement.pdf --sed "s/[0-9]{4}-[0-9]{4}/XXXX-XXXX/g" --head 30
```
