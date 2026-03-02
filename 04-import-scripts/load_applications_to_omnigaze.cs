/*
 * Phase 3: Kamstrup Application Loader for OmniGaze
 * ==================================================
 * 
 * This file is designed to be integrated into OmniGaze as a one-time import service.
 * It reads the JSON output from import_applications.py and populates the FactSheetContainer.
 * 
 * To use:
 * 1. Run import_applications.py first to generate the JSON files in output/
 * 2. Copy this class into OmniGaze project (or reference from a console app)
 * 3. Call KamstrupApplicationLoader.LoadAll() from an admin endpoint or startup hook
 * 
 * Alternatively, the JSON files can be imported via the MCP API using CreateFactSheet
 * tool calls for each application.
 */

using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Linq;
using System.Text.Json;
using OmniGaze.Model.EnterpriseArchitecture;
using OmniGaze.Model.LeanIX;

namespace OmniGaze.Services.Import.Kamstrup
{
    /// <summary>
    /// Loads Kamstrup application data from JSON files produced by import_applications.py
    /// into the OmniGaze FactSheetContainer.
    /// </summary>
    public static class KamstrupApplicationLoader
    {
        private static readonly string DefaultBasePath = @"F:\RootContext\Kamstrup\import-scripts\output";

        /// <summary>
        /// Loads all Kamstrup applications (active + removed) and providers.
        /// Call this once from an admin endpoint or startup hook.
        /// </summary>
        /// <param name="basePath">Path to the output directory containing JSON files</param>
        /// <returns>Import result summary</returns>
        public static KamstrupImportResult LoadAll(string basePath = null)
        {
            basePath ??= DefaultBasePath;
            var result = new KamstrupImportResult();
            var container = FactSheetContainer.Instance;

            try
            {
                // 1. Load custom column definitions first
                var customColPath = Path.Combine(basePath, "custom_column_definitions.json");
                if (File.Exists(customColPath))
                {
                    LoadCustomColumnDefinitions(customColPath, result);
                }

                // 2. Load providers
                var providersPath = Path.Combine(basePath, "providers_extracted.json");
                if (File.Exists(providersPath))
                {
                    LoadProviders(providersPath, container, result);
                }

                // 3. Load active applications
                var activePath = Path.Combine(basePath, "applications_active.json");
                if (File.Exists(activePath))
                {
                    LoadApplications(activePath, container, result, isRetired: false);
                }

                // 4. Load removed applications
                var removedPath = Path.Combine(basePath, "applications_removed.json");
                if (File.Exists(removedPath))
                {
                    LoadApplications(removedPath, container, result, isRetired: true);
                }

                // 5. Resolve hierarchy relationships (set HierarchyChildrenIds)
                ResolveHierarchy(container, result);

                // 6. Save
                FactSheetContainer.Save();
                result.Success = true;
                result.Message = $"Import complete: {result.ActiveAppsLoaded} active + {result.RemovedAppsLoaded} removed apps, {result.ProvidersLoaded} providers";
            }
            catch (Exception ex)
            {
                result.Success = false;
                result.Message = $"Import failed: {ex.Message}";
                result.Errors.Add(ex.ToString());
            }

            return result;
        }

        private static void LoadCustomColumnDefinitions(string path, KamstrupImportResult result)
        {
            var json = File.ReadAllText(path);
            var definitions = JsonSerializer.Deserialize<List<CustomColumnDefJson>>(json);

            var settings = CustomerSettings.Instance;
            if (settings == null)
            {
                result.Warnings.Add("CustomerSettings.Instance is null, cannot create custom columns");
                return;
            }

            foreach (var def in definitions)
            {
                var colId = Guid.Parse(def.Id);
                // Check if already exists
                var existing = settings.CustomColumnDefinitions?.FirstOrDefault(c => c.Id == colId);
                if (existing != null)
                {
                    result.Warnings.Add($"Custom column '{def.Name}' already exists, skipping");
                    continue;
                }

                var colDef = new CustomColumnDefinition
                {
                    Id = colId,
                    Name = def.Name,
                    Description = def.Description,
                    FactSheetType = def.FactSheetType,
                    FieldType = Enum.TryParse<CustomFieldType>(def.FieldType, out var ft) ? ft : CustomFieldType.Text,
                    Required = def.Required,
                    DisplayOrder = def.DisplayOrder,
                    VisibleByDefault = def.VisibleByDefault,
                    AllowedValues = def.AllowedValues ?? new List<string>(),
                };

                settings.CustomColumnDefinitions ??= new List<CustomColumnDefinition>();
                settings.CustomColumnDefinitions.Add(colDef);
                result.CustomColumnsCreated++;
            }
        }

        private static void LoadProviders(string path, FactSheetContainer container, KamstrupImportResult result)
        {
            var json = File.ReadAllText(path);
            var providers = JsonSerializer.Deserialize<List<ProviderJson>>(json);

            foreach (var p in providers)
            {
                var guid = Guid.Parse(p.Id);
                // Check for existing provider with same name
                var existing = container.ProviderFactSheets.FirstOrDefault(
                    x => x.DisplayName.Equals(p.DisplayName, StringComparison.OrdinalIgnoreCase));

                if (existing != null)
                {
                    result.Warnings.Add($"Provider '{p.DisplayName}' already exists (ID: {existing.Id}), skipping");
                    continue;
                }

                var provider = new ProviderFactSheet
                {
                    Id = guid,
                    DisplayName = p.DisplayName,
                    ProviderType = p.ProviderType,
                    CreationMetadata = new FactSheetCreationMetadata
                    {
                        Source = CreationSource.CSVImport,
                        CreatedAt = DateTime.Now,
                        CreatedBy = "KamstrupImport",
                        SourceIdentifier = p.CreationMetadata?.SourceIdentifier ?? "Kamstrup vendor extraction",
                    }
                };

                container.AddIfNotExists(provider);
                result.ProvidersLoaded++;
            }
        }

        private static void LoadApplications(string path, FactSheetContainer container, KamstrupImportResult result, bool isRetired)
        {
            var json = File.ReadAllText(path);
            var apps = JsonSerializer.Deserialize<List<ApplicationJson>>(json, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });

            foreach (var appJson in apps)
            {
                try
                {
                    var guid = Guid.Parse(appJson.Id);

                    // Check for existing app with same name
                    var existing = container.ApplicationFactSheets.FirstOrDefault(
                        x => x.DisplayName.Equals(appJson.DisplayName, StringComparison.OrdinalIgnoreCase));

                    if (existing != null)
                    {
                        result.Warnings.Add($"Application '{appJson.DisplayName}' already exists (ID: {existing.Id}), skipping");
                        result.Skipped++;
                        continue;
                    }

                    var app = new ApplicationFactSheet
                    {
                        Id = guid,
                        DisplayName = appJson.DisplayName,
                        Category = appJson.Category ?? "",
                        RichDescription = appJson.RichDescription,
                        Url = appJson.Url,
                        Responsible = appJson.Responsible,
                        Retired = appJson.Retired,
                        IsBusinessApplication = true,
                    };

                    // LifeCycle
                    if (appJson.LifeCycle != null)
                    {
                        app.LifeCycle = new LifeCycle();
                        if (DateTime.TryParse(appJson.LifeCycle.Plan, out var plan)) app.LifeCycle.Plan = plan;
                        if (DateTime.TryParse(appJson.LifeCycle.PhaseIn, out var phaseIn)) app.LifeCycle.PhaseIn = phaseIn;
                        if (DateTime.TryParse(appJson.LifeCycle.Active, out var active)) app.LifeCycle.Active = active;
                        if (DateTime.TryParse(appJson.LifeCycle.PhaseOut, out var phaseOut)) app.LifeCycle.PhaseOut = phaseOut;
                        if (DateTime.TryParse(appJson.LifeCycle.EndOfLife, out var eol)) app.LifeCycle.EndOfLife = eol;
                    }

                    // LifecycleStage label
                    app.LifecycleStage = appJson.LifecycleStage;

                    // PortFolioStrategy (TIME)
                    if (appJson.PortFolioStrategy?.TIME != null)
                    {
                        if (Enum.TryParse<PortFolioStrategy.StrategyEnum>(appJson.PortFolioStrategy.TIME, out var time))
                        {
                            app.PortFolioStrategy = new PortFolioStrategy { TIME = time };
                        }
                    }

                    // HostedOn
                    if (appJson.HostedOn?.Criticality != null)
                    {
                        if (Enum.TryParse<Hosting.HostingTypeEnum>(appJson.HostedOn.Criticality, out var hostEnum))
                        {
                            app.HostedOn = new Hosting
                            {
                                Criticality = hostEnum,
                                HostingTypeValue = appJson.HostedOn.HostingTypeValue,
                                HostingTypeDescription = appJson.HostedOn.HostingTypeDescription,
                            };
                        }
                    }

                    // ApplicationTypeTags
                    if (appJson.ApplicationTypeTags != null)
                    {
                        app.ApplicationTypeTags = appJson.ApplicationTypeTags.Where(t => t != null).ToList();
                    }

                    // PlatformTags
                    if (appJson.PlatformTags != null)
                    {
                        app.PlatformTags = appJson.PlatformTags.Where(t => t != null).ToList();
                    }

                    // OrganizationTags
                    if (appJson.OrganizationTags != null)
                    {
                        app.OrganizationTags = appJson.OrganizationTags.Where(t => t != null).ToList();
                    }

                    // UserBase
                    if (appJson.UserBase != null)
                    {
                        app.UserBase = new UserBase();
                        if (Enum.TryParse<UserBaseSize>(appJson.UserBase.Size, out var ubSize))
                            app.UserBase.Size = ubSize;
                        app.UserBase.Description = appJson.UserBase.Description;
                    }

                    // AIClassification
                    if (appJson.AIClassification != null)
                    {
                        app.AIClassification = new AIClassification
                        {
                            UsesAI = appJson.AIClassification.UsesAI,
                        };
                        if (Enum.TryParse<AIRiskLevel>(appJson.AIClassification.RiskLevel, out var risk))
                            app.AIClassification.RiskLevel = risk;
                    }

                    // SecurityAssessment
                    if (appJson.SecurityAssessment != null)
                    {
                        app.SecurityAssessment = new SecurityAssessment();
                        if (Enum.TryParse<SecurityStatus>(appJson.SecurityAssessment.Status, out var secStatus))
                            app.SecurityAssessment.Status = secStatus;
                        if (DateTime.TryParse(appJson.SecurityAssessment.ApprovedDate, out var secDate))
                            app.SecurityAssessment.ApprovedDate = secDate;
                        if (Enum.TryParse<SecurityDebtLevel>(appJson.SecurityAssessment.DebtLevel, out var debt))
                            app.SecurityAssessment.DebtLevel = debt;
                    }

                    // Owners
                    if (appJson.Owners != null)
                    {
                        app.Owners = appJson.Owners.Select(o => new OwnerAssignment
                        {
                            Role = o.Role,
                            ExternalName = o.ExternalName,
                            AssignedDate = DateTime.TryParse(o.AssignedDate, out var ad) ? ad : DateTime.Now,
                        }).ToList();
                    }

                    // SuccessorId
                    if (appJson.SuccessorId != null)
                    {
                        app.SuccessorId = appJson.SuccessorId
                            .Where(s => Guid.TryParse(s, out _))
                            .Select(s => Guid.Parse(s))
                            .ToList();
                    }

                    // CustomFields
                    if (appJson.CustomFields != null)
                    {
                        app.CustomFields = appJson.CustomFields
                            .Where(cf => cf.ColumnId != null && cf.Value != null)
                            .Select(cf => new CustomFieldValue(Guid.Parse(cf.ColumnId), cf.Value))
                            .ToList();
                    }

                    // CreationMetadata
                    app.CreationMetadata = new FactSheetCreationMetadata
                    {
                        Source = CreationSource.CSVImport,
                        CreatedAt = DateTime.Now,
                        CreatedBy = "KamstrupImport",
                        SourceIdentifier = appJson.CreationMetadata?.SourceIdentifier ?? $"Kamstrup import: {appJson.DisplayName}",
                        AdditionalMetadata = appJson.CreationMetadata?.AdditionalMetadata ?? new Dictionary<string, string>(),
                    };

                    // Store hierarchy parent ref for later resolution
                    if (!string.IsNullOrEmpty(appJson._HierarchyParentId))
                    {
                        app.CreationMetadata.AdditionalMetadata["_HierarchyParentId"] = appJson._HierarchyParentId;
                    }

                    container.AddIfNotExists(app);

                    if (isRetired)
                        result.RemovedAppsLoaded++;
                    else
                        result.ActiveAppsLoaded++;
                }
                catch (Exception ex)
                {
                    result.Errors.Add($"Failed to import '{appJson?.DisplayName}': {ex.Message}");
                }
            }
        }

        /// <summary>
        /// Resolves hierarchy relationships after all apps are loaded.
        /// Reads _HierarchyParentId from CreationMetadata.AdditionalMetadata
        /// and sets HierarchyChildrenIds on parent apps.
        /// </summary>
        private static void ResolveHierarchy(FactSheetContainer container, KamstrupImportResult result)
        {
            foreach (var app in container.ApplicationFactSheets)
            {
                var parentIdStr = app.CreationMetadata?.AdditionalMetadata?.GetValueOrDefault("_HierarchyParentId");
                if (string.IsNullOrEmpty(parentIdStr) || !Guid.TryParse(parentIdStr, out var parentId))
                    continue;

                var parent = container.ApplicationFactSheets.FirstOrDefault(a => a.Id == parentId);
                if (parent != null)
                {
                    if (!parent.HierarchyChildrenIds.Contains(app.Id))
                    {
                        parent.HierarchyChildrenIds.Add(app.Id);
                        result.HierarchyLinksResolved++;
                    }
                }
                else
                {
                    result.Warnings.Add($"Hierarchy parent {parentId} not found for app '{app.DisplayName}'");
                }
            }
        }
    }

    /// <summary>
    /// Result of the Kamstrup import operation
    /// </summary>
    public class KamstrupImportResult
    {
        public bool Success { get; set; }
        public string Message { get; set; }
        public int ActiveAppsLoaded { get; set; }
        public int RemovedAppsLoaded { get; set; }
        public int ProvidersLoaded { get; set; }
        public int CustomColumnsCreated { get; set; }
        public int HierarchyLinksResolved { get; set; }
        public int Skipped { get; set; }
        public List<string> Warnings { get; set; } = new List<string>();
        public List<string> Errors { get; set; } = new List<string>();
    }

    // ─── JSON DTOs ────────────────────────────────────────────────────────

    public class ApplicationJson
    {
        public string Id { get; set; }
        public string DisplayName { get; set; }
        public string Category { get; set; }
        public string RichDescription { get; set; }
        public string Url { get; set; }
        public string Responsible { get; set; }
        public bool Retired { get; set; }
        public LifeCycleJson LifeCycle { get; set; }
        public string LifecycleStage { get; set; }
        public PortFolioStrategyJson PortFolioStrategy { get; set; }
        public HostingJson HostedOn { get; set; }
        public List<string> ApplicationTypeTags { get; set; }
        public List<string> PlatformTags { get; set; }
        public List<string> OrganizationTags { get; set; }
        public UserBaseJson UserBase { get; set; }
        public AIClassificationJson AIClassification { get; set; }
        public SecurityAssessmentJson SecurityAssessment { get; set; }
        public List<OwnerJson> Owners { get; set; }
        public List<string> SuccessorId { get; set; }
        public List<CustomFieldJson> CustomFields { get; set; }
        public CreationMetadataJson CreationMetadata { get; set; }
        public List<string> HierarchyChildrenIds { get; set; }
        public string _HierarchyParentId { get; set; }
    }

    public class LifeCycleJson
    {
        public string Plan { get; set; }
        public string PhaseIn { get; set; }
        public string Active { get; set; }
        public string PhaseOut { get; set; }
        public string EndOfLife { get; set; }
    }

    public class PortFolioStrategyJson
    {
        public string TIME { get; set; }
        public string Description { get; set; }
    }

    public class HostingJson
    {
        public string Criticality { get; set; }
        public string HostingTypeValue { get; set; }
        public string HostingTypeDescription { get; set; }
    }

    public class UserBaseJson
    {
        public string Size { get; set; }
        public int? Count { get; set; }
        public string Description { get; set; }
        public string UserType { get; set; }
    }

    public class AIClassificationJson
    {
        public bool UsesAI { get; set; }
        public string RiskLevel { get; set; }
        public string ReviewStatus { get; set; }
        public string AICapabilities { get; set; }
        public string ReviewDate { get; set; }
    }

    public class SecurityAssessmentJson
    {
        public string Status { get; set; }
        public string ApprovedDate { get; set; }
        public string NextReviewDate { get; set; }
        public string DebtLevel { get; set; }
        public string Notes { get; set; }
    }

    public class OwnerJson
    {
        public string Role { get; set; }
        public string ExternalName { get; set; }
        public string AssignedDate { get; set; }
    }

    public class CustomFieldJson
    {
        public string ColumnId { get; set; }
        public string Value { get; set; }
    }

    public class CreationMetadataJson
    {
        public string Source { get; set; }
        public string CreatedAt { get; set; }
        public string CreatedBy { get; set; }
        public string SourceIdentifier { get; set; }
        public Dictionary<string, string> AdditionalMetadata { get; set; }
    }

    public class ProviderJson
    {
        public string Id { get; set; }
        public string DisplayName { get; set; }
        public string ProviderType { get; set; }
        public CreationMetadataJson CreationMetadata { get; set; }
    }

    public class CustomColumnDefJson
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string FactSheetType { get; set; }
        public string FieldType { get; set; }
        public bool Required { get; set; }
        public List<string> AllowedValues { get; set; }
        public int DisplayOrder { get; set; }
        public bool VisibleByDefault { get; set; }
    }
}
