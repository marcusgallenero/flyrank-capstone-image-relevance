# Build Log

A log of where AI helped throughtout the project

## Pexels Scraper Script

**Where AI Helped:** General outline of code, and final revisions.

**Where it was Wrong:** In revising my code, I was told to write

```Python
with open(save_path, 'w') as f: # Error in this line (line 34 in script)
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
```

**What I Changed:**

This piece became:

```Python
with open(save_path, 'wb') as f: # Changed to 'wb' because we are writing a .jpg file
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
```
