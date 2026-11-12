// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "AgentAuthorityNative", defaultLocalization: "de", platforms: [.macOS(.v12)],
    products: [.executable(name: "AgentAuthorityMac", targets: ["AgentAuthorityMac"])],
    targets: [
        .target(name: "NativeSupport", publicHeadersPath: "include", cSettings: [.unsafeFlags(["-fobjc-arc"])], linkerSettings: [.linkedFramework("Security")]),
        .target(name: "AuthorityCore", resources: [.process("Resources")]),
        .executableTarget(name: "AgentAuthorityMac", dependencies: ["AuthorityCore", "NativeSupport"], resources: [.copy("Resources/ProductHeader")]),
        .testTarget(name: "AuthorityCoreTests", dependencies: ["AuthorityCore"]),
        .testTarget(name: "MacAppTests", dependencies: ["AgentAuthorityMac"])
    ]
)
