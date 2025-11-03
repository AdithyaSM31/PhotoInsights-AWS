// AWS Configuration
const CONFIG = {
    region: 'us-east-1',
    
    cognito: {
        userPoolId: 'us-east-1_EhhMCMyy3',
        clientId: '75nhnrf91vn97odvmfe31onqra',
        region: 'us-east-1'
    },
    
    api: {
        baseUrl: 'https://fjr24hbqvb.execute-api.us-east-1.amazonaws.com/prod',
        endpoints: {
            upload: '/upload',
            images: '/images',
            search: '/images/search',
            delete: '/images'  // + /{imageId}
        }
    },
    
    s3: {
        uploadsBucket: 'photogallery-uploads-23brs1079',
        processedBucket: 'photogallery-processed-23brs1079'
    }
};
