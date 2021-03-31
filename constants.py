
ROUNDING_PRECISION = 3

QUERY1 = '''
{
  allFactSheets(factSheetType: Application) {
    edges {
      node {
        displayName
        ... on Application {
          relApplicationToUserGroup{
            edges{
              node{
                usageType 
                description
              }
            }
          }
        }
      }
    }
  }
}
'''

QUERY2 = """{
      allFactSheets(factSheetType: Application) {
        edges {
          node {
            name
            completion {
              completion
              percentage
                        }
            }
          }
        }
    }"""

