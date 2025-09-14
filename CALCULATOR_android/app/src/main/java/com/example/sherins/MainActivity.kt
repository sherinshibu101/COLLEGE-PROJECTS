package com.example.sherins

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            CalculatorApp()
        }
    }
}

@Composable
fun CalculatorApp() {
    var display by remember { mutableStateOf("0") }
    var operand1 by remember { mutableStateOf(0.0) }
    var operand2 by remember { mutableStateOf(0.0) }
    var operator by remember { mutableStateOf("") }
    var waitingForOperand by remember { mutableStateOf(false) }

    // Your roll number - CHANGE THIS TO YOUR ACTUAL ROLL NUMBER
    val rollNumber = "22355" // Replace with your roll number

    // History feature
    var calculationHistory by remember { mutableStateOf(listOf<String>()) }
    val dateFormatter = SimpleDateFormat("HH:mm:ss", Locale.getDefault())

    // Colors matching the Swing version
    val headerBackground = Color(0xFF663399)        // Deep Purple
    val buttonPanelBackground = Color(0xFFF0E6FA)   // Light Purple
    val numberButtonColor = Color(0xFF9370DB)       // Medium Purple (same as operators)
    val operatorButtonColor = Color(0xFF9370DB)     // Medium Purple
    val myRButtonColor = Color(0xFF800080)          // Classic Purple
    val functionButtonColor = Color(0xFFB0C4DE)     // Light Steel Blue
    val historyBackground = Color(0xFFF8F5FF)       // Very Light Purple
    val historyTextBackground = Color(0xFFFAF5FF)   // Ghost White Purple
    val clearHistoryButtonColor = Color(0xFF9932CC) // Dark Orchid

    fun addToHistory(calculation: String) {
        val timestamp = dateFormatter.format(Date())
        val historyEntry = "[$timestamp] $calculation"

        val newHistory = calculationHistory.toMutableList()
        newHistory.add(historyEntry)

        // Keep only the last 5 calculations
        if (newHistory.size > 5) {
            newHistory.removeAt(0)
        }

        calculationHistory = newHistory
    }

    fun performCalculation(op1: Double, op2: Double, oper: String): Double {
        return when (oper) {
            "+" -> op1 + op2
            "-" -> op1 - op2
            "×" -> op1 * op2
            "÷" -> if (op2 != 0.0) op1 / op2 else {
                display = "Error"
                addToHistory("⚠️ ERROR: Division by zero attempted")
                0.0
            }
            else -> op2
        }
    }

    fun formatResult(result: Double): String {
        return if (result == result.toInt().toDouble()) {
            result.toInt().toString()
        } else {
            String.format("%.6f", result).trimEnd('0').trimEnd('.')
        }
    }

    fun inputNumber(number: String) {
        if (waitingForOperand) {
            display = number
            waitingForOperand = false
        } else {
            display = if (display == "0") number else display + number
        }
    }

    fun inputDecimal() {
        if (waitingForOperand) {
            display = "0."
            waitingForOperand = false
        } else if (!display.contains(".")) {
            display += "."
        }
    }

    fun inputOperator(nextOperator: String) {
        val inputValue = display.toDoubleOrNull() ?: 0.0

        if (operator.isEmpty()) {
            operand1 = inputValue
        } else if (!waitingForOperand) {
            operand2 = inputValue
            val result = performCalculation(operand1, operand2, operator)
            display = formatResult(result)
            operand1 = result
        }

        waitingForOperand = true
        operator = nextOperator
    }

    fun calculate() {
        if (operator.isNotEmpty() && !waitingForOperand) {
            operand2 = display.toDoubleOrNull() ?: 0.0
            val result = performCalculation(operand1, operand2, operator)
            display = formatResult(result)

            // Add to history
            val calculationString = "${formatResult(operand1)} $operator ${formatResult(operand2)} = ${formatResult(result)}"
            addToHistory(calculationString)

            operator = ""
            waitingForOperand = true
        }
    }

    fun clear() {
        display = "0"
        operand1 = 0.0
        operand2 = 0.0
        operator = ""
        waitingForOperand = false
        addToHistory("🔄 Calculator cleared")
    }

    fun backspace() {
        val current = display
        if (current.length > 1 && current != "Error") {
            display = current.dropLast(1)
        } else {
            display = "0"
        }
    }

    fun plusMinus() {
        val current = display.toDoubleOrNull()
        if (current != null) {
            display = formatResult(-current)
        }
    }

    fun myRFunction() {
        val digits = rollNumber.filter { it.isDigit() }.take(5)

        if (digits.length >= 5) {
            val digitList = digits.map { it.toString().toInt() }
            val sum = digitList.sum()
            display = sum.toString()

            val digitBreakdown = digitList.joinToString(" + ")
            addToHistory("🎯 MyR: $digitBreakdown = $sum")

            operator = ""
            waitingForOperand = true
        } else {
            display = "Error"
            addToHistory("❌ MyR Error: Insufficient digits in roll number")
        }
    }

    fun clearHistory() {
        calculationHistory = emptyList()
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
                text = "Calculator by Sherin Shibu", // Change to your name
                color = Color.White,
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center
            )
        }

        // Display Section - Removed unnecessary spacing
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(100.dp)
                .background(Color.White)
                .padding(16.dp),
            contentAlignment = Alignment.CenterEnd
        ) {
            Text(
                text = display,
                color = Color.Black,
                fontSize = 36.sp,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.End
            )
        }

        // Button Grid - Increased weight to fill more space
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .background(buttonPanelBackground)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            val buttonRows = listOf(
                listOf("C", "⌫", "MyR", "÷"),
                listOf("7", "8", "9", "×"),
                listOf("4", "5", "6", "-"),
                listOf("1", "2", "3", "+"),
                listOf("0", ".", "±", "=")
            )

            buttonRows.forEach { row ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    row.forEach { buttonText ->
                        val backgroundColor = when {
                            buttonText.matches(Regex("[0-9.]")) -> numberButtonColor
                            buttonText in arrayOf("+", "-", "×", "÷", "=") -> operatorButtonColor
                            buttonText == "MyR" -> myRButtonColor
                            else -> functionButtonColor
                        }

                        val textColor = when {
                            buttonText.matches(Regex("[0-9.]")) -> Color.White
                            buttonText in arrayOf("+", "-", "×", "÷", "=") -> Color.White
                            buttonText == "MyR" -> Color.White
                            else -> Color.Black
                        }

                        CalculatorButton(
                            text = buttonText,
                            backgroundColor = backgroundColor,
                            textColor = textColor,
                            modifier = Modifier.weight(1f)
                        ) {
                            when (buttonText) {
                                in "0".."9" -> inputNumber(buttonText)
                                "." -> inputDecimal()
                                "+", "-", "×", "÷" -> inputOperator(buttonText)
                                "=" -> calculate()
                                "C" -> clear()
                                "⌫" -> backspace()
                                "±" -> plusMinus()
                                "MyR" -> myRFunction()
                            }
                        }
                    }
                }
            }
        }

        // History Section - Optimized height
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .height(160.dp)
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
                    text = "📊 Calculation History (Last 5)",
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
                if (calculationHistory.isEmpty()) {
                    Text(
                        text = "📝 No calculations yet. Start calculating to see history!",
                        color = Color(0xFF4B0082),
                        fontSize = 10.sp,
                        fontFamily = FontFamily.Monospace
                    )
                } else {
                    Column(
                        modifier = Modifier.verticalScroll(rememberScrollState())
                    ) {
                        Text(
                            text = "📊 Recent Calculations:",
                            color = Color(0xFF4B0082),
                            fontSize = 10.sp,
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.Bold
                        )

                        Spacer(modifier = Modifier.height(4.dp))

                        calculationHistory.reversed().forEach { entry ->
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
fun CalculatorButton(
    text: String,
    backgroundColor: Color,
    textColor: Color = Color.White,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    Box(
        contentAlignment = Alignment.Center,
        modifier = modifier
            .aspectRatio(1f)
            .background(backgroundColor, RoundedCornerShape(12.dp))
            .clickable { onClick() }
    ) {
        Text(
            text = text,
            color = textColor,
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold
        )
    }
}