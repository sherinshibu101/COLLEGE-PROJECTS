package com.example.imagedownloader

import android.Manifest
import android.content.ContentValues
import android.content.Context
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.drawable.BitmapDrawable
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import coil.ImageLoader
import coil.compose.AsyncImage
import coil.request.ImageRequest
import coil.request.SuccessResult
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ImageDownloaderApp()
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ImageDownloaderApp() {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    
    // State variables
    var imageUrl by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    var downloadHistory by remember { mutableStateOf(listOf<String>()) }
    var statusMessage by remember { mutableStateOf("Enter an image URL to download") }
    var hasStoragePermission by remember { mutableStateOf(false) }
    var lastSavedPath by remember { mutableStateOf("") }
    
    // Date formatter for history
    val dateFormatter = SimpleDateFormat("HH:mm:ss", Locale.getDefault())
    
    // Colors matching the calculator app style
    val headerBackground = Color(0xFF663399)        // Deep Purple
    val buttonPanelBackground = Color(0xFFF0E6FA)   // Light Purple
    val downloadButtonColor = Color(0xFF9370DB)     // Medium Purple
    val clearButtonColor = Color(0xFF800080)        // Classic Purple
    val historyBackground = Color(0xFFF8F5FF)       // Very Light Purple
    val historyTextBackground = Color(0xFFFAF5FF)   // Ghost White Purple
    val clearHistoryButtonColor = Color(0xFF9932CC) // Dark Orchid
    
    // Permission launcher
    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        hasStoragePermission = permissions.values.all { it }
        if (!hasStoragePermission) {
            statusMessage = "❌ Storage permission denied. Cannot save images."
        }
    }
    
    // Check permissions on startup
    LaunchedEffect(Unit) {
        val permissions = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            arrayOf(Manifest.permission.READ_MEDIA_IMAGES)
        } else {
            arrayOf(
                Manifest.permission.WRITE_EXTERNAL_STORAGE,
                Manifest.permission.READ_EXTERNAL_STORAGE
            )
        }
        
        hasStoragePermission = permissions.all { permission ->
            ContextCompat.checkSelfPermission(context, permission) == PackageManager.PERMISSION_GRANTED
        }
        
        if (!hasStoragePermission) {
            permissionLauncher.launch(permissions)
        }
    }
    
    fun addToHistory(message: String) {
        val timestamp = dateFormatter.format(Date())
        val historyEntry = "[$timestamp] $message"
        
        val newHistory = downloadHistory.toMutableList()
        newHistory.add(historyEntry)
        
        // Keep only the last 5 entries
        if (newHistory.size > 5) {
            newHistory.removeAt(0)
        }
        
        downloadHistory = newHistory
    }
    
    fun downloadImage() {
        if (imageUrl.isBlank()) {
            statusMessage = "❌ Please enter a valid image URL"
            return
        }
        
        if (!hasStoragePermission) {
            statusMessage = "❌ Storage permission required to save images"
            return
        }
        
        isLoading = true
        statusMessage = "⏳ Downloading image..."
        
        coroutineScope.launch {
            try {
                val imageLoader = ImageLoader(context)
                val request = ImageRequest.Builder(context)
                    .data(imageUrl)
                    .build()
                
                val result = imageLoader.execute(request)
                
                if (result is SuccessResult) {
                    val bitmap = (result.drawable as BitmapDrawable).bitmap

                    withContext(Dispatchers.IO) {
                        val savedPath = saveImageToGallery(context, bitmap, imageUrl)
                        lastSavedPath = savedPath
                    }

                    statusMessage = "✅ Image downloaded successfully!"
                    addToHistory("✅ Downloaded: ${getFileNameFromUrl(imageUrl)}")
                } else {
                    statusMessage = "❌ Failed to download image. Check URL and try again."
                    addToHistory("❌ Failed to download: ${getFileNameFromUrl(imageUrl)}")
                }
            } catch (e: Exception) {
                statusMessage = "❌ Error: ${e.message}"
                addToHistory("❌ Error downloading: ${getFileNameFromUrl(imageUrl)}")
            } finally {
                isLoading = false
            }
        }
    }
    
    fun clearHistory() {
        downloadHistory = emptyList()
        addToHistory("🔄 History cleared")
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(historyBackground)
    ) {
        // Header Section
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(100.dp)
                .background(headerBackground),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "Image Downloader by Sherin Shibu", // Change to your name
                color = Color.White,
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center
            )
        }
        
        // URL Input Section
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color.White)
                .padding(16.dp)
        ) {
            OutlinedTextField(
                value = imageUrl,
                onValueChange = { imageUrl = it },
                label = { Text("Image URL") },
                placeholder = { Text("https://example.com/image.jpg") },
                modifier = Modifier.fillMaxWidth(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri),
                singleLine = true
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = statusMessage,
                color = when {
                    statusMessage.startsWith("✅") -> Color(0xFF4CAF50)
                    statusMessage.startsWith("❌") -> Color(0xFFF44336)
                    statusMessage.startsWith("⏳") -> Color(0xFFFF9800)
                    else -> Color.Gray
                },
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium
            )

            // Show file path when image is downloaded
            if (lastSavedPath.isNotBlank()) {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "📁 Saved to: $lastSavedPath",
                    color = Color(0xFF2196F3),
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium,
                    modifier = Modifier.padding(horizontal = 4.dp)
                )
            }
        }
        
        // Image Preview Section - Made Much Larger!
        if (imageUrl.isNotBlank() && imageUrl.startsWith("http")) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(400.dp) // Increased from 200dp to 400dp
                    .background(Color.White)
                    .padding(16.dp),
                contentAlignment = Alignment.Center
            ) {
                AsyncImage(
                    model = imageUrl,
                    contentDescription = "Image Preview",
                    modifier = Modifier
                        .fillMaxSize()
                        .background(Color.Gray.copy(alpha = 0.1f), RoundedCornerShape(8.dp)),
                    contentScale = ContentScale.Fit
                )
            }
        }
        
        // Button Section
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(buttonPanelBackground)
                .padding(16.dp)
        ) {
            // First row - Download and Clear buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                DownloadButton(
                    text = if (isLoading) "⏳ Downloading..." else "📥 Download Image",
                    backgroundColor = downloadButtonColor,
                    enabled = !isLoading && imageUrl.isNotBlank(),
                    modifier = Modifier.weight(1f)
                ) {
                    downloadImage()
                }

                DownloadButton(
                    text = "🗑️ Clear URL",
                    backgroundColor = clearButtonColor,
                    enabled = !isLoading,
                    modifier = Modifier.weight(1f)
                ) {
                    imageUrl = ""
                    statusMessage = "Enter an image URL to download"
                    lastSavedPath = "" // Clear the saved path when clearing URL
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Second row - Exit button
            DownloadButton(
                text = "🚪 Exit App",
                backgroundColor = Color(0xFFE91E63), // Pink color for exit
                enabled = !isLoading,
                modifier = Modifier.fillMaxWidth()
            ) {
                (context as? ComponentActivity)?.finish()
            }
        }
        
        // History Section
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .background(historyBackground)
                .padding(12.dp)
        ) {
            // History Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "📊 Download History (Last 5)",
                    color = Color(0xFF663399),
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold
                )
                
                Button(
                    onClick = { clearHistory() },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = clearHistoryButtonColor
                    ),
                    modifier = Modifier
                        .height(28.dp)
                        .wrapContentWidth(),
                    contentPadding = PaddingValues(horizontal = 8.dp, vertical = 0.dp)
                ) {
                    Text(
                        text = "🗑️ Clear",
                        color = Color.White,
                        fontSize = 9.sp
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(6.dp))
            
            // History Content
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(historyTextBackground, RoundedCornerShape(6.dp))
                    .padding(8.dp)
            ) {
                if (downloadHistory.isEmpty()) {
                    Text(
                        text = "📝 No downloads yet. Start downloading images to see history!",
                        color = Color(0xFF4B0082),
                        fontSize = 10.sp,
                        fontFamily = FontFamily.Monospace
                    )
                } else {
                    Column(
                        modifier = Modifier.verticalScroll(rememberScrollState())
                    ) {
                        Text(
                            text = "📊 Recent Downloads:",
                            color = Color(0xFF4B0082),
                            fontSize = 10.sp,
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.Bold
                        )
                        
                        Spacer(modifier = Modifier.height(4.dp))
                        
                        downloadHistory.reversed().forEach { entry ->
                            Text(
                                text = entry,
                                color = Color(0xFF4B0082),
                                fontSize = 9.sp,
                                fontFamily = FontFamily.Monospace
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun DownloadButton(
    text: String,
    backgroundColor: Color,
    enabled: Boolean = true,
    textColor: Color = Color.White,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    Box(
        contentAlignment = Alignment.Center,
        modifier = modifier
            .height(50.dp)
            .background(
                if (enabled) backgroundColor else backgroundColor.copy(alpha = 0.5f),
                RoundedCornerShape(12.dp)
            )
            .clickable(enabled = enabled) { onClick() }
    ) {
        Text(
            text = text,
            color = if (enabled) textColor else textColor.copy(alpha = 0.5f),
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center
        )
    }
}

private fun getFileNameFromUrl(url: String): String {
    return try {
        val fileName = url.substringAfterLast("/")
        if (fileName.contains(".")) fileName else "image_${System.currentTimeMillis()}.jpg"
    } catch (e: Exception) {
        "image_${System.currentTimeMillis()}.jpg"
    }
}

private suspend fun saveImageToGallery(context: Context, bitmap: Bitmap, url: String): String {
    val filename = getFileNameFromUrl(url)

    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
        // Use MediaStore for Android 10+
        val contentValues = ContentValues().apply {
            put(MediaStore.MediaColumns.DISPLAY_NAME, filename)
            put(MediaStore.MediaColumns.MIME_TYPE, "image/jpeg")
            put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_PICTURES + "/ImageDownloader")
        }

        val uri = context.contentResolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, contentValues)
        uri?.let {
            context.contentResolver.openOutputStream(it)?.use { outputStream ->
                bitmap.compress(Bitmap.CompressFormat.JPEG, 100, outputStream)
            }
        }
        "Pictures/ImageDownloader/$filename (in Gallery)"
    } else {
        // Use legacy storage for older versions
        val picturesDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES)
        val imageDownloaderDir = File(picturesDir, "ImageDownloader")
        if (!imageDownloaderDir.exists()) {
            imageDownloaderDir.mkdirs()
        }

        val file = File(imageDownloaderDir, filename)
        FileOutputStream(file).use { outputStream ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, 100, outputStream)
        }
        file.absolutePath
    }
}
