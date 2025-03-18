module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-pass-type-neptune-autominor-true.sentinel"
  }
}

test {
    rules = {
        main = true
    }
}
