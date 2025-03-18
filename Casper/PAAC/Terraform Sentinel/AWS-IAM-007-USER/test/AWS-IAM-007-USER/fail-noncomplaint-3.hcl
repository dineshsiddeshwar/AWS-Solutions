module "tfplan-functions" {

    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"

}

mock "tfplan/v2" {

  module {

    source = "mock-tfplan-v2-fail-noncomplaint-3.sentinel"

  }

}

test {

    rules = {

        main = false

    }

}