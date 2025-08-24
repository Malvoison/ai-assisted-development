# BlastRadius.DotNet (PoC)

Extracts *public* symbol declarations from changed C# files using Roslyn and outputs one JSON object per line.

## Build & Run (locally)

```bash
dotnet build
printf "%s
" src/Project/File1.cs src/Project/File2.cs > changed.txt
dotnet run --project tools/BlastRadius.DotNet/BlastRadius.DotNet.csproj   ./YourSolution.sln changed.txt > symbols.jsonl
```

The output `symbols.jsonl` contains records with fields:
`lang, kind, name, container, signature, file, line, project, assembly, publicSurface`.
