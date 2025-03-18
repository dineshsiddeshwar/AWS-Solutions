module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-pass-missing-attribute-auto-minor-version-upgrade.sentinel"
  }
}

test {
    rules = {
        main = true
    }
}
