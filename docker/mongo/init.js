// FabriX-QA MongoDB Initialization
// Creates the defect metadata collection with schema validation

db = db.getSiblingDB('fabrix_defects');

db.createCollection('defect_images', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['defect_record_id', 'timestamp', 'image_base64', 'heatmap_base64'],
      properties: {
        defect_record_id: { bsonType: 'int', description: 'FK to PostgreSQL defect_records.id' },
        timestamp: { bsonType: 'date' },
        image_base64: { bsonType: 'string', description: 'Base64-encoded defect frame crop' },
        heatmap_base64: { bsonType: 'string', description: 'Base64-encoded Grad-CAM overlay' },
        metadata: {
          bsonType: 'object',
          properties: {
            defect_type: { bsonType: 'string' },
            confidence: { bsonType: 'double' },
            bbox: { bsonType: 'array' },
            production_line_id: { bsonType: 'int' }
          }
        }
      }
    }
  }
});

db.defect_images.createIndex({ defect_record_id: 1 });
db.defect_images.createIndex({ timestamp: -1 });
print('[FabriX-QA] MongoDB initialized successfully.');
