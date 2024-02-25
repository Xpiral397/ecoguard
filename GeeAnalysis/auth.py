import ee

def authenticateEcoGuardProject():
    # credentials = ee.ServiceAccountCredentials('gdsc-solution-2024@gdsc-solution-challenge-413220.iam.gserviceaccount.com', 'client-key.json')
  ee.Authenticate()
  ee.Initialize(project='eco-guard')
  
    
