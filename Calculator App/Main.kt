import javax.swing.*
import java.awt.*
import java.awt.event.ActionEvent
import java.awt.event.ActionListener
import java.text.SimpleDateFormat
import java.util.*

class CalculatorApp : JFrame(), ActionListener {
    private val display = JTextField()
    private val instructionLabel = JLabel()
    private var operand1 = 0.0
    private var operand2 = 0.0
    private var operator = ""
    private var waitingForOperand = false

    private val rollNumber = "22355" // Replace with your roll number

    private val calculationHistory = mutableListOf<String>()
    private val historyTextArea = JTextArea()
    private val historyScrollPane = JScrollPane()
    private val dateFormatter = SimpleDateFormat("HH:mm:ss")

    init {
        createGUI()
        updateInstructions()
        setupHistoryPanel()
    }

    private fun createGUI() {
        title = "Calculator"
        defaultCloseOperation = JFrame.EXIT_ON_CLOSE
        layout = BorderLayout()

        isResizable = false
        setSize(450, 700)
        setLocationRelativeTo(null)

        val headerPanel = JPanel()
        headerPanel.background = Color(102, 51, 153)
        headerPanel.preferredSize = Dimension(450, 60)
        val nameLabel = JLabel("Calculator by Sherin Shibu", SwingConstants.CENTER)
        nameLabel.font = Font("Arial", Font.BOLD, 18)
        nameLabel.foreground = Color(230, 220, 250)
        headerPanel.add(nameLabel)

        val displayPanel = JPanel(BorderLayout())
        displayPanel.preferredSize = Dimension(450, 120)

        display.font = Font("Arial", Font.BOLD, 28)
        display.horizontalAlignment = JTextField.RIGHT
        display.text = "0"
        display.isEditable = false
        display.background = Color(147, 112, 219)
        display.border = BorderFactory.createEmptyBorder(15, 15, 15, 15)
        display.preferredSize = Dimension(420, 70)

        instructionLabel.font = Font("Arial", Font.PLAIN, 14)
        instructionLabel.horizontalAlignment = SwingConstants.CENTER
        instructionLabel.background = Color(241, 243, 244)
        instructionLabel.isOpaque = true
        instructionLabel.border = BorderFactory.createEmptyBorder(10, 10, 10, 10)
        instructionLabel.preferredSize = Dimension(420, 50)

        displayPanel.add(display, BorderLayout.NORTH)
        displayPanel.add(instructionLabel, BorderLayout.SOUTH)

        add(headerPanel, BorderLayout.NORTH)
        add(displayPanel, BorderLayout.CENTER)

        val mainPanel = JPanel(BorderLayout())

        val buttonPanel = JPanel(GridLayout(5, 4, 5, 5))
        buttonPanel.background = Color(240, 230, 250)
        buttonPanel.border = BorderFactory.createEmptyBorder(15, 15, 15, 15)

        val buttonTexts = arrayOf(
            "C", "⌫", "MyR", "÷",
            "7", "8", "9", "×",
            "4", "5", "6", "-",
            "1", "2", "3", "+",
            "0", ".", "±", "="
        )

        for (text in buttonTexts) {
            val button = createButton(text)
            buttonPanel.add(button)
        }

        mainPanel.add(buttonPanel, BorderLayout.CENTER)
        mainPanel.add(createHistoryPanel(), BorderLayout.SOUTH)

        add(mainPanel, BorderLayout.SOUTH)
    }

    private fun createHistoryPanel(): JPanel {
        val historyPanel = JPanel(BorderLayout())
        historyPanel.preferredSize = Dimension(450, 150)
        historyPanel.background = Color(240, 230, 250)
        historyPanel.border = BorderFactory.createTitledBorder(
            BorderFactory.createLineBorder(Color(189, 195, 199), 1),
            "📊 Calculation History (Last 5)",
            0, 0,
            Font("Arial", Font.BOLD, 12),
            Color(52, 73, 94)
        )

        historyTextArea.font = Font("Courier New", Font.PLAIN, 11)
        historyTextArea.isEditable = false
        historyTextArea.background = Color(248, 245, 255)
        historyTextArea.foreground = Color(147, 112, 219)
        historyTextArea.text = "📝 No calculations yet. Start calculating to see history!\n"
        historyTextArea.margin = Insets(8, 8, 8, 8)

        historyScrollPane.setViewportView(historyTextArea)
        historyScrollPane.verticalScrollBarPolicy = JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED
        historyScrollPane.horizontalScrollBarPolicy = JScrollPane.HORIZONTAL_SCROLLBAR_NEVER

        val clearHistoryBtn = JButton("🗑️ Clear History")
        clearHistoryBtn.font = Font("Arial", Font.PLAIN, 10)
        clearHistoryBtn.background = Color(153, 50, 204)
        clearHistoryBtn.foreground = Color(248, 245, 255)
        clearHistoryBtn.preferredSize = Dimension(120, 25)
        clearHistoryBtn.addActionListener { clearHistory() }

        val buttonPanel = JPanel(FlowLayout(FlowLayout.RIGHT))
        buttonPanel.background = Color(248, 249, 250)
        buttonPanel.add(clearHistoryBtn)

        historyPanel.add(historyScrollPane, BorderLayout.CENTER)
        historyPanel.add(buttonPanel, BorderLayout.SOUTH)

        return historyPanel
    }

    private fun setupHistoryPanel() {
        updateHistoryDisplay()
    }

    private fun createButton(text: String): JButton {
        val button = JButton(text)
        button.font = Font("Arial", Font.BOLD, 18)
        button.addActionListener(this)
        button.preferredSize = Dimension(90, 70)
        button.isFocusPainted = false

        when {
            text.matches(Regex("[0-9.]")) -> {
                button.background = Color.WHITE
                button.foreground = Color(147, 112, 219)
            }
            text in arrayOf("+", "-", "×", "÷", "=") -> {
                button.background = Color(147, 112, 219)
                button.foreground = Color.WHITE
            }
            text == "MyR" -> {
                button.background = Color(128, 0, 128)
                button.foreground = Color.WHITE
            }
            else -> {
                button.background = Color(176, 196, 222)
                button.foreground = Color.BLACK
            }
        }

        return button
    }

    private fun updateInstructions() {
        // Remove instruction text
        instructionLabel.text = ""
    }

    override fun actionPerformed(e: ActionEvent) {
        val command = (e.source as JButton).text

        when {
            command.matches(Regex("[0-9]")) -> inputNumber(command)
            command == "." -> inputDecimal()
            command in arrayOf("+", "-", "×", "÷") -> inputOperator(command)
            command == "=" -> calculate()
            command == "C" -> clear()
            command == "⌫" -> backspace()
            command == "±" -> plusMinus()
            command == "MyR" -> myRFunction()
        }

        updateInstructions()
    }

    private fun inputNumber(number: String) {
        if (waitingForOperand) {
            display.text = number
            waitingForOperand = false
        } else {
            display.text = if (display.text == "0") number else display.text + number
        }
        showFeedback("Number '$number' entered. Current value: ${display.text}")
    }

    private fun inputDecimal() {
        if (waitingForOperand) {
            display.text = "0."
            waitingForOperand = false
        } else if (!display.text.contains(".")) {
            display.text += "."
        }
        showFeedback("Decimal point added")
    }

    private fun inputOperator(nextOperator: String) {
        val inputValue = display.text.toDoubleOrNull() ?: 0.0

        if (operator.isEmpty()) {
            operand1 = inputValue
            showFeedback("First number: $inputValue, Operation: $nextOperator selected")
        } else if (!waitingForOperand) {
            operand2 = inputValue
            val result = performCalculation()
            display.text = formatResult(result)
            operand1 = result
            showFeedback("Calculated: ${formatResult(operand1)} $operator ${formatResult(operand2)} = ${formatResult(result)}")
        }

        waitingForOperand = true
        operator = nextOperator
    }

    private fun calculate() {
        if (operator.isNotEmpty() && !waitingForOperand) {
            operand2 = display.text.toDoubleOrNull() ?: 0.0
            val result = performCalculation()
            display.text = formatResult(result)

            val calculationString = "${formatResult(operand1)} $operator ${formatResult(operand2)} = ${formatResult(result)}"
            addToHistory(calculationString)

            showFeedback("Final Result: $calculationString")
            operator = ""
            waitingForOperand = true
        } else {
            showFeedback("Please complete the calculation steps first!")
        }
    }

    private fun performCalculation(): Double {
        return when (operator) {
            "+" -> operand1 + operand2
            "-" -> operand1 - operand2
            "×" -> operand1 * operand2
            "÷" -> if (operand2 != 0.0) operand1 / operand2 else {
                showFeedback("Error: Cannot divide by zero!")
                display.text = "Error"
                addToHistory("⚠️ ERROR: Division by zero attempted")
                0.0
            }
            else -> operand2
        }
    }

    private fun formatResult(result: Double): String {
        return if (result == result.toInt().toDouble()) {
            result.toInt().toString()
        } else {
            String.format("%.6f", result).trimEnd('0').trimEnd('.')
        }
    }

    private fun clear() {
        display.text = "0"
        operand1 = 0.0
        operand2 = 0.0
        operator = ""
        waitingForOperand = false
        showFeedback("Calculator cleared. Ready for new calculation!")
        addToHistory("🔄 Calculator cleared")
    }

    private fun backspace() {
        val current = display.text
        if (current.length > 1 && current != "Error") {
            display.text = current.dropLast(1)
            showFeedback("Last digit removed")
        } else {
            display.text = "0"
            showFeedback("Display reset to 0")
        }
    }

    private fun plusMinus() {
        val current = display.text.toDoubleOrNull()
        if (current != null) {
            display.text = formatResult(-current)
            showFeedback("Sign changed to: ${display.text}")
        }
    }

    private fun myRFunction() {
        val digits = rollNumber.filter { it.isDigit() }.take(5)

        if (digits.length >= 5) {
            val digitList = digits.map { it.toString().toInt() }
            val sum = digitList.sum()
            display.text = sum.toString()

            val digitBreakdown = digitList.joinToString(" + ")

            addToHistory("🎯 MyR: $digitBreakdown = $sum")

            val message = """
                🎯 MyR Function Result:

                🔢 Roll Number: $rollNumber
                📢 First 5 digits: $digitBreakdown
                ➕ Sum: $sum

                ✅ Calculator display updated to: $sum
            """.trimIndent()

            JOptionPane.showMessageDialog(
                this,
                message,
                "MyR Function - Sum of Roll Number Digits",
                JOptionPane.INFORMATION_MESSAGE
            )

            showFeedback("MyR Result: Sum of first 5 digits ($digitBreakdown) = $sum")
            operator = ""
            waitingForOperand = true
        } else {
            val errorMessage = """
                ❌ MyR Function Error:

                Roll number must contain at least 5 digits!

                Current roll number: $rollNumber
                Digits found: ${digits.length}

                Please update the rollNumber variable in the code.
            """.trimIndent()

            JOptionPane.showMessageDialog(
                this,
                errorMessage,
                "MyR Function Error",
                JOptionPane.ERROR_MESSAGE
            )
            showFeedback("MyR Error: Need at least 5 digits in roll number")
            addToHistory("❌ MyR Error: Insufficient digits in roll number")
        }
    }

    private fun addToHistory(calculation: String) {
        val timestamp = dateFormatter.format(Date())
        val historyEntry = "[$timestamp] $calculation"

        calculationHistory.add(historyEntry)

        if (calculationHistory.size > 5) {
            calculationHistory.removeAt(0)
        }

        updateHistoryDisplay()
    }

    private fun updateHistoryDisplay() {
        if (calculationHistory.isEmpty()) {
            historyTextArea.text = "📝 No calculations yet. Start calculating to see history!\n"
        } else {
            val historyText = StringBuilder("📊 Recent Calculations:\n\n")
            calculationHistory.reversed().forEach { entry ->
                historyText.append("$entry\n")
            }
            historyText.append("\n💡 Tip: Your calculation history is automatically saved!")
            historyTextArea.text = historyText.toString()
        }

        historyTextArea.caretPosition = historyTextArea.document.length
    }

    private fun clearHistory() {
        calculationHistory.clear()
        updateHistoryDisplay()
        JOptionPane.showMessageDialog(
            this,
            "🗑️ History cleared successfully!\n\nAll previous calculations have been removed.",
            "History Cleared",
            JOptionPane.INFORMATION_MESSAGE
        )
    }

    private fun showFeedback(message: String) {
        // Feedback messages handled here (optional to print or log)
    }
}

fun main() {
    SwingUtilities.invokeLater {
        try {
            for (info in UIManager.getInstalledLookAndFeels()) {
                if ("Nimbus" == info.name) {
                    UIManager.setLookAndFeel(info.className)
                    break
                }
            }
        } catch (e: Exception) {
            // Default look and feel will be used
        }

        CalculatorApp().isVisible = true
    }
}

