# CraftMate AI — Minecraft Desktop Assistant

CraftMate is a Windows desktop companion for Minecraft with an AI chat panel, seed/chunk utilities, a local Java slime-chunk scanner, recipe explorer, blueprint layer viewer, JSON import/export, and an always-on-top overlay.

## Windows executable

The GitHub Actions workflow builds a portable `CraftMate.exe` on a Windows runner using PyInstaller. The EXE includes the Python runtime; Python does not need to be installed on the target PC.

After a successful run, open **Actions → Build CraftMate for Windows → latest successful run → Artifacts** and download `CraftMate-Windows`. Extract the ZIP and run `CraftMate.exe`.

## Notes

- Local Minecraft tools work without an API key.
- Online AI requires an OpenAI API key and API billing; this is separate from a ChatGPT subscription.
- The seed utility includes block/chunk/region coordinate conversion and a Java slime-chunk scanner. It is not a full replacement for Chunkbase's version-specific biome/structure finder.
- Windows may still show a reputation warning for unsigned personal builds. Do not disable Windows security to run software you do not trust.
