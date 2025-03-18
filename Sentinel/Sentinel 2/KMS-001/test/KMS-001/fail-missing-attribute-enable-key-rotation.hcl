module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-fail-missing-attribute-enable-key-rotation.sentinel"
  }
}

test {
    rules = {
        main = false
    }
}
