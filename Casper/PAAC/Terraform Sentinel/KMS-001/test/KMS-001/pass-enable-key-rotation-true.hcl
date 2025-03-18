module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-pass-enable-key-rotation-true.sentinel"
  }
}

test {
    rules = {
        main = true
    }
}
