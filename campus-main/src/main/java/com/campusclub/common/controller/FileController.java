package com.campusclub.common.controller;

import com.campusclub.dto.ApiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.UUID;

@Slf4j
@RestController
@RequestMapping({"/v1/upload", "/upload"})
public class FileController {

    @Value("${upload.dir:uploads}")
    private String uploadDir;

    @Value("${upload.base-url:}")
    private String baseUrl;

    @PostMapping
    public ResponseEntity<ApiResponse<String>> uploadFile(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body(ApiResponse.error("请选择要上传的文件"));
        }

        try {
            // 创建上传目录
            String dateDir = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMM"));
            Path uploadPath = Paths.get(uploadDir, dateDir);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }

            // 生成唯一文件名
            String originalFilename = file.getOriginalFilename();
            String extension = originalFilename != null ?
                    originalFilename.substring(originalFilename.lastIndexOf(".")) : ".jpg";
            String newFilename = UUID.randomUUID() + extension;

            // 保存文件
            Path filePath = uploadPath.resolve(newFilename);
            Files.copy(file.getInputStream(), filePath);

            // 生成访问URL
            String fileUrl = baseUrl.isEmpty() ?
                    "/uploads/" + dateDir + "/" + newFilename :
                    baseUrl + "/uploads/" + dateDir + "/" + newFilename;

            log.info("文件上传成功: {}", fileUrl);
            return ResponseEntity.ok(ApiResponse.success("上传成功", fileUrl));

        } catch (IOException e) {
            log.error("文件上传失败", e);
            return ResponseEntity.internalServerError()
                    .body(ApiResponse.error("文件上传失败: " + e.getMessage()));
        }
    }
}
