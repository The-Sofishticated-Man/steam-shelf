# Integration Tests

This project includes comprehensive integration tests that verify the Steam API endpoints and file storage functionality.

## Running Integration Tests

### Run all integration tests:

```bash
python -m pytest -m integration
```

### Run all tests (including integration):

```bash
python -m pytest
```

### Run integration tests with verbose output:

```bash
python -m pytest -m integration -v
```

### Skip integration tests (run only unit tests):

```bash
python -m pytest -m "not integration"
```

## Integration Test Coverage

The integration tests cover:

### 1. **Steam API Endpoint Verification** (`test_steam_api_endpoint_real`)

- Tests actual Steam CDN endpoints with a known game (Counter-Strike 2, ID: 730)
- Verifies all image types: library_600x900_2x.jpg, library_hero.jpg, logo.png, capsule_616x353.jpg
- Checks HTTP response codes and content types
- Ensures images are actually downloadable from Steam's servers

### 2. **Error Handling** (`test_steam_api_404_handling`)

- Tests Steam API behavior with non-existent game IDs
- Verifies proper error status codes (404 or 502)
- Ensures the system handles Steam API errors gracefully

### 3. **Real Image Download and File Storage** (`test_image_client_real_download_and_file_storage`)

- Downloads actual images from Steam CDN
- Verifies files are saved with correct shortcut ID naming scheme
- Checks file integrity (non-empty, valid image headers)
- Tests JPEG and PNG format validation

### 4. **Standalone Function Testing** (`test_standalone_function_real_download`)

- Tests the `save_images_from_id()` standalone function
- Verifies backward compatibility with existing API
- Uses generated shortcut IDs for file naming

### 5. **Directory Creation and Permissions** (`test_directory_creation_and_permissions`)

- Tests automatic directory structure creation
- Verifies nested path handling (userdata/123456/config/grid)
- Checks file permissions and read/write access
- Ensures proper Steam directory structure

### 6. **Error Handling with Invalid Games** (`test_error_handling_with_invalid_game_id`)

- Tests exception handling for non-existent game IDs
- Verifies no partial files are created on errors
- Ensures clean failure without side effects

### 7. **End-to-End Workflow** (`test_end_to_end_workflow_with_real_data`)

- Complete integration test with real Steam database
- Tests game discovery → shortcut generation → image downloading workflow
- Uses actual Steam games (Counter-Strike 2, Team Fortress 2, Dota 2)
- Verifies shortcut ID generation and file naming consistency

## Test Requirements

### Network Dependencies:

- Internet connection required for Steam CDN access
- Tests use well-known Steam games that should always be available
- Timeouts are set to 10 seconds for network requests

### File System:

- Tests use temporary directories (`tmp_path` fixture)
- No permanent files are created during testing
- Tests verify proper directory creation and permissions

## Known Limitations

- Integration tests may be slower due to network requests
- Tests depend on Steam's CDN being available
- Some tests use specific game IDs that must exist on Steam

## Troubleshooting

If integration tests fail:

1. **Network Issues**: Check internet connection and Steam CDN availability
2. **Game ID Changes**: If Steam removes test games, update game IDs in tests
3. **API Changes**: If Steam changes their CDN structure, update URLs in tests
4. **File Permissions**: Ensure write access to temporary directories

## Test Data

The integration tests use these known Steam games:

- Counter-Strike 2 (ID: 730) - Primary test game
- Team Fortress 2 (ID: 440) - Secondary test game
- Dota 2 (ID: 570) - Secondary test game

These games are chosen because they:

- Are major Steam titles unlikely to be removed
- Have complete artwork sets
- Are free-to-play (widely accessible)
