import Foundation

/// ThreadDesk principle: stable keys, complete DE/EN catalogs, explicit preference first.
/// Independent catalog and preference domain; no runtime imports from other products.
public final class Localization {
    public static let shared = Localization()
    public static let languages = ["de", "en"]
    public static let changed = Notification.Name("AgentAuthorityLanguageChanged")
    public let catalog: [String: [String: String]]
    public private(set) var language: String
    public private(set) var preference: String
    public static func normalize(_ value: String) -> String {
        let code = value.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
            .replacingOccurrences(of: "_", with: "-").split(separator: "-").first.map(String.init) ?? "de"
        return languages.contains(code) ? code : "de"
    }
    public static func resolve(explicit: String?, saved: String?, environment: [String: String], preferred: [String]) -> String {
        if let v = explicit, v != "system" { return normalize(v) }
        if let v = saved, v != "system" { return normalize(v) }
        for key in ["AGENT_AUTHORITY_LANG", "LC_ALL", "LC_MESSAGES", "LANG"] {
            if let raw = environment[key], !raw.isEmpty {
                let base = raw.components(separatedBy: ".")[0].components(separatedBy: "@")[0]
                if ["c", "posix"].contains(base.lowercased()) { continue }
                return normalize(base)
            }
        }
        for value in preferred {
            let code = value.lowercased().replacingOccurrences(of: "_", with: "-").split(separator: "-").first.map(String.init) ?? ""
            if languages.contains(code) { return code }
        }
        return "de"
    }
    public init(explicit: String? = nil, defaults: UserDefaults = .standard) {
        let url = Bundle.main.url(forResource: "Strings", withExtension: "json", subdirectory: "AuthorityCore")
            ?? Bundle.module.url(forResource: "Strings", withExtension: "json")!
        catalog = try! JSONDecoder().decode([String: [String: String]].self, from: Data(contentsOf: url))
        preference = explicit ?? defaults.string(forKey: "language") ?? "system"
        language = Self.resolve(explicit: explicit, saved: defaults.string(forKey: "language"),
            environment: ProcessInfo.processInfo.environment, preferred: Locale.preferredLanguages)
    }
    public func choose(_ value: String, persist: Bool = true) {
        preference = value == "system" ? value : Self.normalize(value)
        if persist { UserDefaults.standard.set(preference, forKey: "language") }
        language = Self.resolve(explicit: preference, saved: nil, environment: ProcessInfo.processInfo.environment, preferred: Locale.preferredLanguages)
        NotificationCenter.default.post(name: Self.changed, object: nil)
    }
    public func text(_ key: String, _ values: [String: String] = [:]) -> String {
        guard var text = catalog[key]?[language] else { return "⟦\(key)⟧" }
        for (name, value) in values { text = text.replacingOccurrences(of: "{\(name)}", with: value) }
        return text
    }
}
public func L(_ key: String, _ values: [String: String] = [:]) -> String { Localization.shared.text(key, values) }
