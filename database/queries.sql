-- Get fee details for a student

SELECT
    StudentID,
    Name,
    Email,
    Course,
    TotalFee,
    PaidAmount,
    (TotalFee - PaidAmount) AS OutstandingAmount,
    DueDate
FROM Students
WHERE StudentID = 'STU001';

-- Find overdue students

SELECT
    StudentID,
    Name,
    Email,
    TotalFee,
    PaidAmount,
    (TotalFee - PaidAmount) AS OutstandingAmount,
    DueDate
FROM Students
WHERE DueDate < CAST(GETDATE() AS DATE)
  AND PaidAmount < TotalFee;

-- Update a student's paid amount

UPDATE Students
SET PaidAmount = 80000.00
WHERE StudentID = 'STU003';