# OmniGaze — Azure Data Source Permissions Guide

**Prepared for:** Kristian @ Kamstrup  
**Date:** 2 March 2026  
**Document version:** 1.0

---

## Table of Contents

1. [Overview & Recommended Setup](#1-overview--recommended-setup)
2. [Log Analytics (Azure Monitor)](#2-log-analytics-azure-monitor)
3. [Microsoft Defender for Endpoint (MDE)](#3-microsoft-defender-for-endpoint-mde)
4. [Intune (Microsoft Endpoint Manager)](#4-intune-microsoft-endpoint-manager)
5. [Azure Monitor Agent (AMA) — Status & Data Collection Rules](#5-azure-monitor-agent-ama--status--data-collection-rules)
6. [Azure Resource Manager (Subscriptions, Resources, Tags)](#6-azure-resource-manager-subscriptions-resources-tags)
7. [Entra ID vs On-Prem AD Assessment](#7-entra-id-vs-on-prem-ad-assessment)
8. [Consolidated Permission Summary](#8-consolidated-permission-summary)
9. [Gaps & Recommendations](#9-gaps--recommendations)

---

## 1. Overview & Recommended Setup

### App Registration Architecture

**Recommended:** A **single multi-tenant App Registration** in the customer's Entra ID tenant (or OmniGaze's tenant for multi-tenant scenarios) with all required permissions.

OmniGaze already uses this model — a single `AzureCredential` object per tenant with:
- `TenantId`, `ClientId`, `Secret` (client credentials flow)
- Feature flags: `EnableDefenderIntegration`, `EnableLogAnalyticsIntegration`, etc.

**Why single app?**
- Simpler consent process (one admin consent per customer)
- Single secret/certificate to manage
- Unified audit trail in Entra ID sign-in logs
- OmniGaze already stores one credential set per tenant

### Authentication Flow

OmniGaze uses **OAuth 2.0 Client Credentials** (app-only, no user interaction):
- **MDE:** `ConfidentialClientApplication` → token for `https://api.securitycenter.microsoft.com/.default`
- **Log Analytics:** `ClientSecretCredential` → Azure SDK `LogsQueryClient`
- **Graph/Intune:** `ClientSecretCredential` → token for `https://graph.microsoft.com/.default`
- **Azure ARM:** `ClientSecretCredential` → Azure SDK ARM clients

### What Kamstrup Needs to Do

1. Create an App Registration in their Entra ID tenant (or consent to OmniGaze's multi-tenant app)
2. Grant **Admin Consent** for the API permissions listed below
3. Assign **Azure RBAC roles** at the appropriate scope (subscription/resource group/workspace) for ARM-based APIs
4. Provide OmniGaze with: `TenantId`, `ClientId`, `ClientSecret`, `SubscriptionId`, `LAWorkspaceId`

---

## 2. Log Analytics (Azure Monitor)

### What OmniGaze Does Today

OmniGaze already has full Log Analytics integration via `LogAnalyticsClient.cs`. It uses the **Azure Monitor Query SDK** (`Azure.Monitor.Query.LogsQueryClient`) to run KQL queries against Log Analytics workspaces.

**Current data collected:**
| Data Source | KQL Table | Purpose |
|---|---|---|
| VM Computer inventory | `VMComputer` | Server discovery, OS, hardware |
| VM Connections | `VMConnection` | Dependency mapping between servers |
| VM Processes | `VMProcess` | Process-level application mapping |
| IIS Logs | `W3CIISLog` | Web server traffic analysis |
| MDE Device Info | `DeviceInfo` | Sentinel device discovery, risk/exposure |
| MDE Network Info | `DeviceNetworkInfo` | MAC addresses, IP addresses per device |
| MDE Network Events | `DeviceNetworkEvents` | Process-level connection data from MDE |
| MDE Vulnerabilities | `DeviceTvmSoftwareVulnerabilities` | Per-device vulnerability counts |

### Required Permissions

| Permission / Role | Type | Scope | Why Needed |
|---|---|---|---|
| **Log Analytics Reader** | Azure RBAC Role | Workspace or Resource Group | Read-only access to query Log Analytics workspace data via `LogsQueryClient` |
| *Alternative:* **Monitoring Reader** | Azure RBAC Role | Subscription | Broader read access to all monitoring data across the subscription |

**API Details:**
- **API:** Azure Monitor Query API (`https://api.loganalytics.io/v1/workspaces/{workspaceId}/query`)
- **SDK:** `Azure.Monitor.Query` NuGet package (used by OmniGaze)
- **Auth scope:** `https://api.loganalytics.io/.default`
- **No Microsoft Graph permissions needed** for Log Analytics — this uses Azure ARM/Monitor RBAC

### How to Assign

```
# Assign Log Analytics Reader at workspace level (most restrictive)
az role assignment create \
  --assignee <app-client-id> \
  --role "Log Analytics Reader" \
  --scope /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<workspace-name>
```

---

## 3. Microsoft Defender for Endpoint (MDE)

### What OmniGaze Does Today

OmniGaze has full MDE integration via `DefenderApiClient.cs`, which calls the **MDE REST API** directly at `https://api.securitycenter.microsoft.com/api/v1.0/`.

**Current data collected:**
| Endpoint | Data | Purpose |
|---|---|---|
| `/api/v1.0/alerts` | Security alerts | Active threat detection |
| `/api/v1.0/machines` | Device inventory | Machine list with health status |
| `/api/v1.0/software` | Software inventory | Installed software across fleet |
| `/api/v1.0/exposureScore` | Exposure score | Organization security posture |
| `/api/v1.0/indicators` | Threat intel indicators | Custom IOCs |
| `/api/v1.0/vulnerabilities` | Vulnerability list | Known CVEs across devices |

Additionally, OmniGaze queries MDE tables through **Sentinel/Log Analytics** (DeviceInfo, DeviceNetworkInfo, DeviceNetworkEvents, DeviceTvmSoftwareVulnerabilities) for richer data.

### Required Permissions — MDE API (WindowsDefenderATP)

| Permission | Type | Why Needed |
|---|---|---|
| `Machine.Read.All` | Application | Read device inventory, health status, onboarding status |
| `Alert.Read.All` | Application | Read security alerts |
| `Software.Read.All` | Application | Read software inventory across devices |
| `Vulnerability.Read.All` | Application | Read known vulnerabilities |
| `Score.Read.All` | Application | Read exposure/secure score |
| `Ti.ReadWrite` | Application | Read threat intelligence indicators (OmniGaze reads only) |

**API Details:**
- **API resource:** `WindowsDefenderATP` (search in "APIs my organization uses")
- **Base URL:** `https://api.securitycenter.microsoft.com`
- **Auth scope:** `https://api.securitycenter.microsoft.com/.default`
- **Token audience:** Must be `https://api.securitycenter.microsoft.com` (some APIs reject `api.security.microsoft.com` tokens)

### How to Assign

1. In the App Registration → **API permissions** → **Add a permission**
2. Select **APIs my organization uses** → search **WindowsDefenderATP**
3. Select **Application permissions** → check the permissions above
4. Click **Grant admin consent**

> **Note:** If Kamstrup also sends MDE data to a Sentinel workspace, the Log Analytics Reader role (Section 2) covers querying MDE tables via KQL. The MDE API permissions above are for the *direct* MDE API.

---

## 4. Intune (Microsoft Endpoint Manager)

### What OmniGaze Does Today

OmniGaze has extensive Intune integration via `LightweightGraphClient.cs` and `IntuneDeviceMerger.cs`. It uses the **Microsoft Graph API** to fetch:

| Graph Endpoint | Data | Purpose |
|---|---|---|
| `/devices` | Azure AD device objects | Device inventory, compliance, management status |
| `/deviceManagement/managedDevices` | Intune managed devices | MAC addresses, serial numbers, storage, UPN, hardware |
| `/deviceManagement/detectedApps` | Detected applications | Software inventory from Intune |
| `/deviceManagement/detectedApps/{id}/managedDevices` | App-to-device mapping | Which devices have which apps |
| `/deviceManagement/windowsMalwareInformation` | Malware detections | Windows Defender malware findings |
| `/deviceManagement/windowsMalwareInformation/{id}/deviceMalwareStates` | Per-device malware state | Malware status per affected device |

### Required Permissions — Microsoft Graph

| Permission | Type | Why Needed |
|---|---|---|
| `Device.Read.All` | Application | Read Azure AD device objects (compliance, management status, OS info) |
| `DeviceManagementManagedDevices.Read.All` | Application | Read Intune managed devices (MAC, serial, storage, UPN, malware info) |
| `DeviceManagementApps.Read.All` | Application | Read Intune detected apps and app-to-device mappings |

**API Details:**
- **API:** Microsoft Graph v1.0
- **Base URL:** `https://graph.microsoft.com/v1.0`
- **Auth scope:** `https://graph.microsoft.com/.default`
- **Requires:** Active Intune license in the tenant

### Data Useful for EA (Enterprise Architecture)

| Data Point | Source | EA Value |
|---|---|---|
| Managed devices list | `managedDevices` | Complete device inventory including BYOD |
| Compliance status | `managedDevices.complianceState` | Security posture per device |
| OS versions | `managedDevices.operatingSystem/osVersion` | OS lifecycle management |
| Installed applications | `detectedApps` | Application portfolio mapping |
| App-to-device mapping | `detectedApps/{id}/managedDevices` | Application landscape analysis |
| Primary user per device | `managedDevices.userPrincipalName` | User-to-asset mapping |
| Hardware inventory | `managedDevices` (storage, RAM, arch) | Capacity planning |
| Malware detections | `windowsMalwareInformation` | Security risk assessment |
| Last sync time | `managedDevices.lastSyncDateTime` | Active vs stale device identification |

---

## 5. Azure Monitor Agent (AMA) — Status & Data Collection Rules

### Background: AMA vs MMA (Legacy)

| Feature | AMA (Azure Monitor Agent) | MMA (Log Analytics Agent / Microsoft Monitoring Agent) |
|---|---|---|
| Status | **Current** — actively developed | **Deprecated** — retired August 2024 |
| Configuration | Data Collection Rules (DCRs) — centralized | Workspace-level config — per workspace |
| Authentication | Managed identity (Azure VMs) / Azure Arc | Workspace key or certificate |
| Multi-homing | Supports multiple DCRs per agent | One workspace per agent (or up to 4) |
| On-premises | Requires Azure Arc | Direct agent install |
| VM Insights (dependency mapping) | Supported | Supported (legacy) |

### What OmniGaze Needs from AMA

OmniGaze doesn't talk to AMA directly — it queries the **data that AMA sends to Log Analytics**. However, Kamstrup may want to verify AMA deployment status and DCR configuration.

### Required Permissions — Azure Resource Manager

| Permission / Role | Type | Scope | Why Needed |
|---|---|---|---|
| **Monitoring Reader** | Azure RBAC Role | Subscription or Resource Group | Read AMA extension status on VMs, read DCR configurations |
| *Or more specific:* | | | |
| `Microsoft.Insights/dataCollectionRules/read` | ARM action | Subscription | Read Data Collection Rule definitions |
| `Microsoft.Insights/dataCollectionRuleAssociations/read` | ARM action | Subscription | Read which VMs are associated with which DCRs |
| `Microsoft.Compute/virtualMachines/extensions/read` | ARM action | Subscription | Check if AMA extension is installed on VMs |
| `Microsoft.HybridCompute/machines/extensions/read` | ARM action | Subscription | Check AMA on Azure Arc-connected machines |

**API Details:**
- **API:** Azure Resource Manager REST API
- **Base URL:** `https://management.azure.com`
- **Auth scope:** `https://management.azure.com/.default`
- **SDK:** `Azure.ResourceManager` / `Azure.ResourceManager.Monitor`

### Key ARM Endpoints

```
# List Data Collection Rules
GET /subscriptions/{sub}/providers/Microsoft.Insights/dataCollectionRules?api-version=2022-06-01

# List DCR Associations (which VMs have which DCRs)
GET /subscriptions/{sub}/providers/Microsoft.Insights/dataCollectionRuleAssociations?api-version=2022-06-01

# Check VM extensions (AMA installed?)
GET /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vm}/extensions?api-version=2023-07-01
# Look for: extensionType = "AzureMonitorWindowsAgent" or "AzureMonitorLinuxAgent"
```

---

## 6. Azure Resource Manager (Subscriptions, Resources, Tags)

### What OmniGaze Does Today

OmniGaze scans Azure subscriptions, resource groups, and resources using the Azure SDK (`AzureProvider`, `AzureScanService.cs`). This includes:
- Subscription enumeration
- Resource group listing
- Resource inventory (VMs, databases, storage, etc.)
- Azure tag-based application auto-linking
- Azure retail pricing lookup

### Required Permissions — Azure RBAC

| Role | Scope | Why Needed |
|---|---|---|
| **Reader** | Subscription | Enumerate subscriptions, resource groups, resources, tags |

This is the standard Azure built-in `Reader` role. It gives read-only access to all Azure resources in the subscription without any ability to modify.

---

## 7. Entra ID vs On-Prem AD Assessment

### What OmniGaze Checks Today — On-Prem AD

OmniGaze has a mature on-prem AD assessment via `ActiveDirectoryScanner.cs` using LDAP/DirectoryServices:

| Check | How | Data Used |
|---|---|---|
| **Unused/stale user accounts** | `UnusedAccounts.razor.cs` — filters by `LastLogon` > N days (default 45) | `lastlogontimestamp` from AD |
| **Dead computer objects** | `DeadComputerObjects.razor.cs` — not ping-responsive AND `LastLogon` > N days (default 60) | `lastLogonTimeStamp`, ping result |
| **Disabled accounts** | Checks `userAccountControl` flag `0x0002` (ACCOUNTDISABLE) | AD `userAccountControl` attribute |
| **Password age** | Reads `pwdLastSet` | AD `pwdLastSet` attribute |
| **Group membership** | Reads `memberOf` for each user | AD `memberOf` attribute |
| **Admin accounts** | `Admins.razor` — identifies privileged accounts | Group membership analysis |
| **User security groups** | `UserSecurityGroups.razor` — maps users to security groups | AD group data |
| **Account creation date** | Reads `whenCreated` | AD `whenCreated` attribute |
| **Last modification** | Reads `whenChanged` | AD `whenChanged` attribute |

**AD properties collected per user:** `samAccountName`, `userPrincipalName`, `givenName`, `sn`, `displayName`, `mail`, `lastlogontimestamp`, `pwdLastSet`, `userAccountControl`, `memberOf`, `whenChanged`, `whenCreated`, `distinguishedName`

### Current Entra ID Capabilities

OmniGaze currently uses Entra ID for:
- **Authentication** (OIDC sign-in via `EntraIDConfiguration.cs`)
- **Device enumeration** (via Graph `/devices` — see Section 4)
- **RBAC group resolution** (`ADGroupResolutionService.cs`, `EntraIDGroupMapping.cs`)

**⚠️ OmniGaze does NOT currently perform Entra ID user assessment** (stale accounts, last sign-in, guest users, service principals, conditional access). This is a gap.

### Equivalent Entra ID Checks

| On-Prem AD Check | Entra ID Equivalent | Graph API Property | Status |
|---|---|---|---|
| Unused user accounts (LastLogon > N days) | Last sign-in activity | `user.signInActivity.lastSignInDateTime` | **🔴 Not implemented** |
| Dead computer objects | Stale device objects | `device.approximateLastSignInDateTime` | **🟡 Partially** (device data collected but not assessed) |
| Disabled accounts | Disabled users | `user.accountEnabled` | **🔴 Not implemented** |
| Password age | Password last changed | `user.lastPasswordChangeDateTime` | **🔴 Not implemented** |
| Group membership | Entra ID group membership | `user.memberOf` | **🟡 Partially** (used for RBAC, not assessed) |
| Admin accounts | Privileged role assignments | `directoryRole.members` | **🔴 Not implemented** |
| — | **Unused guest accounts** | `user.userType == 'Guest'` + `signInActivity` | **🔴 Not implemented** |
| — | **Stale service principals** | `servicePrincipal.signInActivity` | **🔴 Not implemented** |
| — | **Conditional access gaps** | `conditionalAccessPolicy` | **🔴 Not implemented** |
| — | **MFA registration status** | `authenticationMethod` | **🔴 Not implemented** |

### Required Graph API Permissions for Entra ID Assessment

| Permission | Type | Why Needed |
|---|---|---|
| `User.Read.All` | Application | Read all user properties (accountEnabled, userType, creation date, etc.) |
| `AuditLog.Read.All` | Application | **Required** to read `signInActivity` property on users (last sign-in dates) |
| `Directory.Read.All` | Application | Read directory roles, group memberships, service principals |
| `Policy.Read.All` | Application | Read conditional access policies (for gap analysis) |
| `UserAuthenticationMethod.Read.All` | Application | Read MFA registration status per user |
| `ServicePrincipalEndpoint.Read.All` | Application | Read service principal details (optional — `Directory.Read.All` may suffice) |

> **Important:** Reading `signInActivity` requires **both** `User.Read.All` and `AuditLog.Read.All`. Additionally, the tenant must have **Entra ID P1 or P2** licensing for sign-in activity data to be available.

### Graph API Query Examples

```http
# Get users with sign-in activity (requires AuditLog.Read.All + User.Read.All)
GET /v1.0/users?$select=displayName,userPrincipalName,accountEnabled,userType,
    createdDateTime,signInActivity,lastPasswordChangeDateTime
    &$filter=signInActivity/lastSignInDateTime le 2025-12-01T00:00:00Z

# Get guest users with sign-in activity
GET /v1.0/users?$select=displayName,userPrincipalName,signInActivity
    &$filter=userType eq 'Guest'

# Get directory role members (privileged accounts)
GET /v1.0/directoryRoles?$expand=members

# Get conditional access policies
GET /v1.0/identity/conditionalAccess/policies
```

---

## 8. Consolidated Permission Summary

### Microsoft Graph API Permissions (Admin Consent Required)

| Permission | Type | Used For |
|---|---|---|
| `Device.Read.All` | Application | Azure AD device inventory |
| `DeviceManagementManagedDevices.Read.All` | Application | Intune managed devices, malware info |
| `DeviceManagementApps.Read.All` | Application | Intune detected applications |
| `User.Read.All` | Application | Entra ID user assessment *(new)* |
| `AuditLog.Read.All` | Application | Sign-in activity for stale account detection *(new)* |
| `Directory.Read.All` | Application | Roles, groups, service principals *(new)* |
| `Policy.Read.All` | Application | Conditional access policy analysis *(new)* |

### WindowsDefenderATP API Permissions

| Permission | Type | Used For |
|---|---|---|
| `Machine.Read.All` | Application | MDE device inventory |
| `Alert.Read.All` | Application | MDE security alerts |
| `Software.Read.All` | Application | MDE software inventory |
| `Vulnerability.Read.All` | Application | MDE vulnerabilities |
| `Score.Read.All` | Application | MDE exposure score |
| `Ti.ReadWrite` | Application | Threat intelligence indicators |

### Azure RBAC Roles

| Role | Scope | Used For |
|---|---|---|
| **Reader** | Subscription | Enumerate Azure resources, resource groups, tags |
| **Log Analytics Reader** | Workspace(s) | Query Log Analytics data (KQL) |
| **Monitoring Reader** | Subscription *(optional)* | Read AMA status, DCRs, monitoring config |

> **Note:** `Reader` at subscription level includes `Monitoring Reader` capabilities. If you only assign `Reader` + `Log Analytics Reader` on the specific workspace(s), that covers most scenarios. Add `Monitoring Reader` if you need explicit AMA/DCR visibility.

---

## 9. Gaps & Recommendations

### Current Gaps in OmniGaze

| Gap | Impact | Effort to Implement |
|---|---|---|
| **No Entra ID user assessment** | Cannot detect stale cloud-only accounts, unused guests, MFA gaps | Medium — need new Graph queries + assessment UI |
| **No service principal assessment** | Cannot detect unused/stale app registrations | Medium |
| **No conditional access analysis** | Cannot identify CA policy gaps | Medium |
| **No AMA deployment status check** | Cannot verify agent deployment coverage | Low — ARM API calls for extensions |
| **MDE API uses legacy URL** | `api.securitycenter.microsoft.com` still works but `api.security.microsoft.com` is the new base | Low — URL update |

### Recommendations for Kamstrup

1. **Start with current permissions** — The Graph + MDE + RBAC permissions above cover all existing OmniGaze functionality
2. **Add Entra ID assessment permissions now** — Even if OmniGaze doesn't have the UI yet, having `User.Read.All` + `AuditLog.Read.All` + `Directory.Read.All` consented means we can build and deploy the feature without re-consenting
3. **Use a single App Registration** — One app with all permissions, one admin consent
4. **Prefer workspace-scoped Log Analytics Reader** over subscription-level to follow least-privilege
5. **Ensure Entra ID P1/P2 licensing** — Required for `signInActivity` data on users

### Quick Setup Checklist for Kamstrup

- [ ] Create App Registration (or consent to OmniGaze multi-tenant app)
- [ ] Add Microsoft Graph permissions (7 permissions listed above)
- [ ] Add WindowsDefenderATP permissions (6 permissions listed above)  
- [ ] Grant admin consent for all API permissions
- [ ] Assign `Reader` role on target subscription(s)
- [ ] Assign `Log Analytics Reader` on target workspace(s)
- [ ] Create client secret (or certificate) and share securely with OmniGaze
- [ ] Provide: Tenant ID, Client ID, Secret, Subscription ID, LA Workspace ID
- [ ] Verify: Intune license active, Entra ID P1/P2 active

---

*Document generated from OmniGaze codebase analysis and Microsoft documentation. All permissions are read-only — OmniGaze does not write to or modify any Azure/Entra ID resources.*
