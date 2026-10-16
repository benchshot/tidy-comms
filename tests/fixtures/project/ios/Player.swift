public protocol PlayerDelegate: AnyObject {
    func playerDidStart(_ player: Player)
    // func playerDidPause(_ player: Player)
}

final class ViewModel {
    func load() {
        // let old = legacyLoad()
        fetch()
    }
}

extension ViewModel: UITableViewDataSource {
    // func numberOfSections(in tableView: UITableView) -> Int { 1 }
}

// public func legacyAPI() -> String
