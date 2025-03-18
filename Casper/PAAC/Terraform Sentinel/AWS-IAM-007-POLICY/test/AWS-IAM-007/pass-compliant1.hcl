module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-v2-pass-compliant1.sentinel"
  }
}

test {
    rules = {
        main = true
    }
}
