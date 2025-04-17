# Diagrams for Typing Tutor Application

## Class Diagram

```mermaid
classDiagram
    class QMainWindow {
        <<PyQt5>>
    }
    class QObject {
        <<PyQt5>>
    }
    class QThread {
        <<PyQt5>>
    }
    
    class Worker {
        +finished: pyqtSignal
        -_should_stop: bool
        +run()
        +stop()
    }
    
    class MyApp {
        +__init__()
        +show_message()
        +goto_registerScreen()
        +goto_homeScreen()
        +goto_resetPasswordVerificationScreen()
    }
    
    class RegisterScreen {
        +__init__()
        +show_message()
        +gotoScreen1()
    }
    
    class TypingScreen {
        -random_200_text: str
        +__init__()
        +gotoPractice()
        +goto_account()
        +thread_cleanup()
        +refresh_typing_text()
        +textChangedfunc(str)
        +thread_timer()
        +worker_progress()
    }
    
    class PracticeScreen {
        +__init__()
        +gotoHome()
        +goto_account()
    }
    
    class ResetPasswordVerificationScreen {
        +__init__()
        +backToLoginScreen()
    }
    
    class AccountScreen {
        +__init__()
        +backToLoginScreen()
    }
    
    class LiveInputChecker {
        -wordindex: int
        -text: str
        -text_browser: QTextBrowser
        -typed_word_lst: list
        -typed_raw_word_lst: list
        -raw_letter_lst: list
        -track_raw_letter_lst: list
        +__init__(text, text_browser)
        +__str__()
        +inputcheck(word)
        +letter_color_confirmed(word_status_dict, context_text)
    }
    
    QObject <|-- Worker
    QMainWindow <|-- MyApp
    QMainWindow <|-- RegisterScreen
    QMainWindow <|-- TypingScreen
    QMainWindow <|-- PracticeScreen
    QMainWindow <|-- ResetPasswordVerificationScreen
    QMainWindow <|-- AccountScreen
    
    TypingScreen ..> LiveInputChecker : uses
    TypingScreen ..> Worker : creates
    TypingScreen ..> QThread : uses
</mermaid>

## Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant App as Application
    participant Login as Login Screen
    participant Register as Register Screen
    participant Typing as Typing Screen
    participant Practice as Practice Screen
    participant Account as Account Screen
    
    User->>App: Start Application
    App->>Login: Initialize
    Login-->>User: Display Login Screen
    
    alt User Registers
        User->>Login: Click Register
        Login->>Register: Navigate to Register Screen
        Register-->>User: Display Register Form
        User->>Register: Enter Registration Details
        Register->>Register: Process Registration
        Register->>Login: Return to Login
    end
    
    User->>Login: Enter Credentials
    User->>Login: Click Login
    Login->>Typing: Navigate to Typing Screen
    Typing-->>User: Display Typing Test
    
    alt User Practices
        User->>Typing: Click Practice
        Typing->>Practice: Navigate to Practice Screen
        Practice-->>User: Display Practice Interface
        User->>Practice: Complete Practice
        Practice->>Typing: Return to Typing Screen
    end
    
    alt User Views Account
        User->>Typing: Click Account
        Typing->>Account: Navigate to Account Screen
        Account-->>User: Display Account Information
        User->>Account: Click Logout
        Account->>Login: Return to Login Screen
    end
    
    alt User Types Test
        User->>Typing: Start Typing
        Typing->>Typing: Start Timer Thread
        User->>Typing: Continue Typing
        Typing->>Typing: Check Input in Real-time
        Typing->>Typing: Update Display with Colored Feedback
        Typing->>Typing: Timer Completes
        Typing-->>User: Display Results
    end
</mermaid>

## Activity Diagram

```mermaid
stateDiagram-v2
    [*] --> LoginScreen
    
    LoginScreen --> RegisterScreen: Click Register
    RegisterScreen --> LoginScreen: Submit/Cancel
    
    LoginScreen --> ResetPasswordScreen: Click Forgot Password
    ResetPasswordScreen --> LoginScreen: Submit/Cancel
    
    LoginScreen --> TypingScreen: Login Success
    
    TypingScreen --> PracticeScreen: Click Practice
    PracticeScreen --> TypingScreen: Return
    
    TypingScreen --> AccountScreen: Click Account
    AccountScreen --> LoginScreen: Logout
    
    state TypingScreen {
        [*] --> Idle
        Idle --> Typing: Start Typing
        Typing --> TimerRunning: First Character
        TimerRunning --> Checking: Continue Typing
        Checking --> Feedback: Check Input
        Feedback --> Checking: Update Display
        Checking --> Complete: Timer Ends
        Complete --> Results: Show Results
        Results --> Idle: Refresh Test
    }
    
    TypingScreen --> [*]: Exit Application
</mermaid>

## Component Diagram

```mermaid
graph TD
    subgraph "UI Components"
        UI[UI Files]
        UI --> Login[login.ui]
        UI --> Register[register.ui]
        UI --> Home[home.ui]
        UI --> Practice[practice.ui]
        UI --> Account[account.ui]
        UI --> ForgotPassword[forgotPasswordVerificationCode.ui]
    end
    
    subgraph "Python Classes"
        PyClasses[Python Classes]
        PyClasses --> MyApp[MyApp]
        PyClasses --> RegisterScreen[RegisterScreen]
        PyClasses --> TypingScreen[TypingScreen]
        PyClasses --> PracticeScreen[PracticeScreen]
        PyClasses --> AccountScreen[AccountScreen]
        PyClasses --> ResetPasswordScreen[ResetPasswordVerificationScreen]
        PyClasses --> Worker[Worker Thread]
    end
    
    subgraph "Core Functionality"
        Core[Core Modules]
        Core --> InputChecker[LiveInputChecker]
        Core --> WordGenerator[Typing Test Words Generator]
    end
    
    subgraph "Data"
        Data[Data Files]
        Data --> TestWords[TestTypingWords]
    end
    
    UI --> PyClasses
    PyClasses --> Core
    Core --> Data
</mermaid>

## Deployment Diagram

```mermaid
graph TD
    subgraph "User's Computer"
        OS[Operating System]
        Python[Python Runtime]
        PyQt[PyQt5 Framework]
        App[Typing Tutor Application]
        
        OS --> Python
        Python --> PyQt
        PyQt --> App
        
        subgraph "Application Components"
            UI[UI Files]
            Code[Python Code]
            Data[Test Words Data]
            
            App --> UI
            App --> Code
            App --> Data
        end
    end
</mermaid>

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> NotLoggedIn
    
    NotLoggedIn --> LoggingIn: Enter Credentials
    LoggingIn --> LoggedIn: Valid Credentials
    LoggingIn --> NotLoggedIn: Invalid Credentials
    
    LoggedIn --> TypingTest: Select Test
    LoggedIn --> PracticeMode: Select Practice
    LoggedIn --> AccountView: View Account
    
    TypingTest --> TestInProgress: Start Typing
    TestInProgress --> TestCompleted: Timer Ends
    TestCompleted --> TypingTest: Refresh Test
    
    PracticeMode --> PracticeInProgress: Start Practice
    PracticeInProgress --> PracticeCompleted: Complete Practice
    PracticeCompleted --> PracticeMode: New Practice
    
    AccountView --> LoggedIn: Return
    
    LoggedIn --> NotLoggedIn: Logout
    
    state TestInProgress {
        [*] --> Typing
        Typing --> Checking: Input Character
        Checking --> Feedback: Validate Input
        Feedback --> Typing: Continue
    }
</mermaid>