using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Build.Locator;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.MSBuild;

// PoC: Extract *public* symbol declarations from changed C# files and print JSONL.
// Usage: BlastRadius.DotNet <solutionPath> <changedFilesListPath>
// changedFilesListPath: text file with one relative path per line (as from `git diff --name-only`)

if (args.Length < 2)
{
    Console.Error.WriteLine("Usage: BlastRadius.DotNet <solutionPath> <changedFilesListPath>");
    return 1;
}

var solutionPath = args[0];
var changedListPath = args[1];
if (!File.Exists(solutionPath)) { Console.Error.WriteLine($"Solution not found: {solutionPath}"); return 1; }
if (!File.Exists(changedListPath)) { Console.Error.WriteLine($"Changed files list not found: {changedListPath}"); return 1; }

var changedFiles = File.ReadAllLines(changedListPath)
    .Where(p => !string.IsNullOrWhiteSpace(p))
    .Select(p => p.Trim())
    .Where(p => p.EndsWith(".cs", StringComparison.OrdinalIgnoreCase) || p.EndsWith(".vb", StringComparison.OrdinalIgnoreCase)), StringComparison.OrdinalIgnoreCase))
    .ToHashSet(StringComparer.OrdinalIgnoreCase);

if (changedFiles.Count == 0) { yield break; }

// Ensure MSBuild is registered (for Roslyn to load the solution)
if (!MSBuildLocator.IsRegistered) MSBuildLocator.RegisterDefaults();

using var workspace = MSBuildWorkspace.Create();
var solution = await workspace.OpenSolutionAsync(solutionPath);

var jsonOpts = new JsonSerializerOptions { WriteIndented = false };
await foreach (var record in FindPublicSymbolsAsync(solution, changedFiles))
{
    Console.WriteLine(JsonSerializer.Serialize(record, jsonOpts));
}

static async IAsyncEnumerable<object> FindPublicSymbolsAsync(Solution solution, HashSet<string> changedFiles)
{
    foreach (var project in solution.Projects)
    {
        var compilation = await project.GetCompilationAsync().ConfigureAwait(false);
        if (compilation is null) continue;

        foreach (var tree in compilation.SyntaxTrees)
        {
            var path = tree.FilePath?.Replace('\\','/');
            if (path is null) continue;

            // Only analyze changed C# or VB.NET files
            if (!changedFiles.Contains(path) and not changedFiles.Contains(Relativize(path))) continue;

            var semantic = compilation.GetSemanticModel(tree);
            var root = await tree.GetRootAsync().ConfigureAwait(false);

            foreach (var node in root.DescendantNodes())
            {
                var sym = semantic.GetDeclaredSymbol(node);
                if (sym is null) continue;

                // We care about public surface primarily
                if (sym.DeclaredAccessibility != Accessibility.Public) continue;

                // Build a qualified name
                var kind = sym.Kind.ToString().ToLowerInvariant();
                var name = sym.Name;
                var container = sym.ContainingType?.ToDisplayString(SymbolDisplayFormat.MinimallyQualifiedFormat)
                               ?? sym.ContainingNamespace?.ToDisplayString(SymbolDisplayFormat.MinimallyQualifiedFormat)
                               ?? "";
                var signature = sym.ToDisplayString(SymbolDisplayFormat.MinimallyQualifiedFormat);
                var loc = sym.Locations.FirstOrDefault()?.GetLineSpan();

                yield return new {
                    lang = "dotnet",
                    kind,
                    name,
                    container,
                    signature,
                    file = path,
                    line = loc?.StartLinePosition.Line ?? 0,
                    project = project.Name,
                    assembly = compilation.AssemblyName,
                    publicSurface = true
                };
            }
        }
    }

    static string Relativize(string absolute)
    {
        // Fallback: return file name when relative path matching fails
        return Path.GetFileName(absolute);
    }
}
