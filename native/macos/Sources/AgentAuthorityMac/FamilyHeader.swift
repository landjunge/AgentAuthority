import AppKit
import AuthorityCore

/// Reuses the existing native five-icon renderer; the split controllers stay alive below it.
final class FamilyHeaderView: LayoutView {
    let products = ProductHeaderView()
    let wordmark = NSTextField(labelWithString: "")
    let language = NSSegmentedControl(labels: ["DE", "EN"], trackingMode: .selectOne, target: nil, action: nil)
    let detail = NSTextField(labelWithString: "")
    override init(frame: NSRect) {
        super.init(frame: frame)
        color = Palette.background
        let name = NSMutableAttributedString(string: "Agent", attributes: [
            .foregroundColor: Palette.wordmark, .font: NSFont.systemFont(ofSize: 21, weight: .bold)])
        name.append(NSAttributedString(string: "Authority", attributes: [
            .foregroundColor: Palette.brand, .font: NSFont.systemFont(ofSize: 21, weight: .bold)]))
        wordmark.attributedStringValue = name; wordmark.setAccessibilityLabel("AgentAuthority")
        language.setWidth(44, forSegment: 0); language.setWidth(44, forSegment: 1)
        language.target = self; language.action = #selector(changeLanguage)
        language.setAccessibilityLabel(L("family.language"))
        detail.font = .systemFont(ofSize: 11); detail.textColor = Palette.muted
        detail.lineBreakMode = .byTruncatingTail; detail.alignment = .center
        products.onDetail = { [weak self] text in self?.showDetail(text) }
        [wordmark, products, language, detail].forEach { addSubview($0) }
        localize()
        arrange = { [weak self] rect in
            guard let self else { return }
            self.wordmark.frame = NSRect(x: 16, y: 8, width: 240, height: 30)
            self.products.frame = NSRect(x: (rect.width-236)/2, y: 0, width: 236, height: 44)
            self.language.frame = NSRect(x: rect.width-112, y: 0, width: 96, height: 44)
            self.detail.frame = NSRect(x: 16, y: 45, width: rect.width-32, height: 16)
        }
    }
    required init?(coder: NSCoder) { fatalError() }
    func localize() {
        language.selectedSegment = Localization.shared.language == "en" ? 1 : 0
        language.setAccessibilityLabel(L("family.language"))
        products.localize(); showDetail(L("app.observer"))
    }
    func showDetail(_ text: String) { detail.stringValue = text; detail.toolTip = text }
    @objc private func changeLanguage() {
        Localization.shared.choose(language.selectedSegment == 1 ? "en" : "de")
    }
}

final class FamilyContentController: NSViewController {
    let header = FamilyHeaderView()
    let split: MainSplitController
    init(split: MainSplitController) { self.split = split; super.init(nibName: nil, bundle: nil) }
    required init?(coder: NSCoder) { fatalError() }
    override func loadView() {
        let root = LayoutView(); root.color = Palette.background; view = root
        addChild(split); root.addSubview(header); root.addSubview(split.view)
        root.arrange = { [weak self] rect in
            guard let self else { return }
            self.header.frame = NSRect(x: 0, y: 0, width: rect.width, height: 64)
            self.split.view.frame = NSRect(x: 0, y: 64, width: rect.width, height: max(0, rect.height-64))
        }
    }
}
