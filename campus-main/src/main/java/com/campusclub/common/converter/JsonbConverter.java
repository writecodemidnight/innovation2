package com.campusclub.common.converter;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;

@Converter
public class JsonbConverter implements AttributeConverter<String, String> {

    private static final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public String convertToDatabaseColumn(String attribute) {
        if (attribute == null || attribute.isEmpty()) {
            return "{}";
        }
        // Ensure it's valid JSON
        try {
            objectMapper.readTree(attribute);
            return attribute;
        } catch (Exception e) {
            // If not valid JSON, wrap it as a string value
            return "\"" + attribute.replace("\"", "\\\"") + "\"";
        }
    }

    @Override
    public String convertToEntityAttribute(String dbData) {
        if (dbData == null || dbData.isEmpty() || dbData.equals("{}")) {
            return null;
        }
        return dbData;
    }
}
