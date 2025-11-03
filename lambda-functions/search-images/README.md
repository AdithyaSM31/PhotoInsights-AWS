# Lambda Function: SearchImages

## Purpose
Search user's photo gallery by tags, filename, date range, and AI analysis results.

## API Endpoint

**GET** `/images/search`

**Headers:**
- `Authorization: Bearer {JWT_TOKEN}`

## Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `tags` | string | Comma-separated tags | `sunset,beach,ocean` |
| `filename` | string | Search in filename | `vacation` |
| `dateFrom` | string | Start date | `2025-01-01` or `1704067200` |
| `dateTo` | string | End date | `2025-12-31` or `1735689600` |
| `hasFaces` | boolean | Filter by face presence | `true` or `false` |
| `hasText` | boolean | Filter by text presence | `true` or `false` |
| `limit` | number | Results per page (1-100) | `20` (default) |
| `sortOrder` | string | Sort order | `desc` (default) or `asc` |
| `lastKey` | string | Pagination token | (from previous response) |

## Search Examples

### Search by Tags
```
GET /images/search?tags=sunset,beach
```
Returns images tagged with "sunset" OR "beach"

### Search by Filename
```
GET /images/search?filename=vacation
```
Returns images with "vacation" in filename

### Search by Date Range
```
GET /images/search?dateFrom=2025-01-01&dateTo=2025-06-30
```
Returns images from first half of 2025

### Search Images with Faces
```
GET /images/search?hasFaces=true
```
Returns only images containing detected faces

### Search Images with Text
```
GET /images/search?hasText=true
```
Returns images with detected text (signs, documents, etc.)

### Combined Search
```
GET /images/search?tags=beach&hasFaces=true&dateFrom=2025-06-01
```
Returns beach photos with faces from June 2025 onwards

## Response Format

```json
{
  "images": [
    {
      "imageId": "550e8400-e29b-41d4-a716-446655440000",
      "imageName": "sunset-beach.jpg",
      "uploadTimestamp": 1699012800,
      "fileSize": 2458624,
      "width": 3840,
      "height": 2160,
      "urls": {
        "thumbnail": "https://cdn.../thumb-uuid.jpg",
        "medium": "https://cdn.../med-uuid.jpg",
        "large": "https://cdn.../uuid.webp",
        "original": "https://s3.../original.jpg"
      },
      "tags": ["sunset", "beach", "ocean", "sky", "nature"],
      "processingStatus": "completed",
      "aiAnalysis": {
        "faceCount": 2,
        "hasText": false,
        "isSafe": true,
        "topLabels": ["sunset", "sky", "beach"]
      }
    }
  ],
  "count": 15,
  "userId": "user-123",
  "hasMore": true,
  "nextKey": "eyJpbWFnZUlkIjoi..."
}
```

## Configuration

### Environment Variables
- `DYNAMODB_TABLE` - Table name (default: PhotoGallery-Images)
- `PROCESSED_BUCKET` - S3 bucket (default: photogallery-processed-23brs1079)
- `CLOUDFRONT_DOMAIN` - CDN domain (optional)

### IAM Permissions Required
- `dynamodb:Query` on table and UploadTimeIndex GSI

### Lambda Configuration
- **Runtime:** Python 3.11
- **Memory:** 256 MB
- **Timeout:** 10 seconds
- **Handler:** lambda_function.lambda_handler

## Query Strategy

### DynamoDB GSI Usage
- Uses `UploadTimeIndex` (userId + uploadTimestamp)
- Efficient time-based sorting and filtering
- Supports ascending/descending order

### Filter Logic
- **Tags:** OR logic (matches ANY tag)
- **Other filters:** AND logic (must match ALL)
- Fetches 3x limit to account for filtering

### Performance
- **With date range:** Fast (uses GSI key condition)
- **Without date range:** Slower (scans all user images)
- **Best practice:** Always include date range for large galleries

## Client Usage Example

### JavaScript/Fetch
```javascript
async function searchImages(criteria) {
  const params = new URLSearchParams(criteria);
  
  const response = await fetch(
    `https://api.example.com/images/search?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${jwtToken}`
      }
    }
  );
  
  return await response.json();
}

// Usage examples

// Search by tag
const sunsets = await searchImages({ tags: 'sunset' });

// Search by multiple tags
const beachSunsets = await searchImages({ 
  tags: 'sunset,beach',
  limit: 50
});

// Search recent photos with faces
const recentWithFaces = await searchImages({
  hasFaces: true,
  dateFrom: '2025-10-01',
  limit: 20
});

// Search by filename
const vacationPhotos = await searchImages({
  filename: 'vacation',
  sortOrder: 'asc'  // Oldest first
});

// Pagination
let allResults = [];
let nextKey = null;

do {
  const response = await searchImages({
    tags: 'travel',
    limit: 20,
    lastKey: nextKey
  });
  
  allResults.push(...response.images);
  nextKey = response.nextKey;
} while (response.hasMore);

console.log(`Total results: ${allResults.length}`);
```

### React Search Component
```jsx
const SearchGallery = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    tags: '',
    hasFaces: null,
    dateFrom: ''
  });
  
  const handleSearch = async () => {
    setLoading(true);
    try {
      const data = await searchImages(filters);
      setResults(data.images);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="search-gallery">
      <input
        type="text"
        placeholder="Tags (sunset, beach...)"
        value={filters.tags}
        onChange={(e) => setFilters({...filters, tags: e.target.value})}
      />
      
      <label>
        <input
          type="checkbox"
          checked={filters.hasFaces === true}
          onChange={(e) => setFilters({
            ...filters, 
            hasFaces: e.target.checked ? true : null
          })}
        />
        Only photos with faces
      </label>
      
      <input
        type="date"
        value={filters.dateFrom}
        onChange={(e) => setFilters({...filters, dateFrom: e.target.value})}
      />
      
      <button onClick={handleSearch} disabled={loading}>
        {loading ? 'Searching...' : 'Search'}
      </button>
      
      <div className="results">
        {results.map(img => (
          <img 
            key={img.imageId} 
            src={img.urls.thumbnail} 
            alt={img.imageName}
          />
        ))}
      </div>
    </div>
  );
};
```

## Deployment

```powershell
cd lambda-functions/search-images
Compress-Archive -Path lambda_function.py -DestinationPath function.zip -Force

aws lambda create-function `
  --function-name PhotoGallery-SearchImages `
  --runtime python3.11 `
  --role arn:aws:iam::799016889364:role/PhotoGalleryLambdaRole `
  --handler lambda_function.lambda_handler `
  --zip-file fileb://function.zip `
  --environment "Variables={DYNAMODB_TABLE=PhotoGallery-Images,PROCESSED_BUCKET=photogallery-processed-23brs1079}" `
  --timeout 10 `
  --memory-size 256 `
  --description "Search images by tags, date, filename, AI analysis"
```

## Performance Optimization

### Best Practices
1. **Always use date ranges** for large galleries (> 1000 images)
2. **Limit results** to 20-50 per page
3. **Cache popular searches** with CloudFront/API Gateway
4. **Index commonly searched tags** separately (future enhancement)

### Query Costs
- **With date filter:** Scans only date range
- **Without date filter:** Scans all user images
- **Cost:** ~$0.00025 per 1000 items scanned

## Limitations

### DynamoDB Constraints
- **1MB query limit:** Pagination automatically handles this
- **Filter expressions:** Applied after query (not as efficient as key conditions)
- **Tag OR logic:** Implemented at application level

### Search Capabilities
- ✓ Exact tag match ("sunset" matches "sunset")
- ✓ Filename contains ("vacation" matches "summer-vacation-2025.jpg")
- ✗ Partial tag match ("sun" does NOT match "sunset")
- ✗ Fuzzy search (no typo tolerance)
- ✗ Full-text search in AI descriptions

## Future Enhancements

- [ ] ElasticSearch integration for full-text search
- [ ] Fuzzy tag matching with Levenshtein distance
- [ ] Search by image similarity (Rekognition)
- [ ] Search by color palette
- [ ] Search by location (EXIF GPS data)
- [ ] Saved searches and filters
- [ ] Search result ranking by relevance
- [ ] Auto-complete for tags
