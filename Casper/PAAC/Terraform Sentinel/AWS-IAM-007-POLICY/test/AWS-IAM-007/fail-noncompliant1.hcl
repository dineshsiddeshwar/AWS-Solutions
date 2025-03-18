module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-v2-fail-noncompliant1.sentinel"
  }
}

test {
    rules = {
        main = false
    }
}
