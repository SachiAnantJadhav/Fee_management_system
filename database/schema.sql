CREATE TABLE Students (
    StudentID VARCHAR(20) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(255) NOT NULL,
    Course VARCHAR(100) NOT NULL,
    TotalFee DECIMAL(10, 2) NOT NULL,
    PaidAmount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    DueDate DATE NOT NULL,

    CONSTRAINT CK_Students_TotalFee
        CHECK (TotalFee >= 0),

    CONSTRAINT CK_Students_PaidAmount
        CHECK (PaidAmount >= 0),

    CONSTRAINT CK_Students_PaidAmount_NotGreaterThanTotal
        CHECK (PaidAmount <= TotalFee)
);

CREATE TABLE Administrators (
    AdminID VARCHAR(20) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Role VARCHAR(50) NOT NULL
);