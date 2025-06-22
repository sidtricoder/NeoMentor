// Test script to verify the data extraction logic
const sampleResponse = {
  "success": true,
  "result": {
    "syllabus": {
      "weekly_schedule": {
        "Week_1": {
          "topics": [
            "Introduction to Machine Learning",
            "Types of Machine Learning (Supervised, Unsupervised, Reinforcement Learning)",
            "Data Preprocessing Techniques (Cleaning, Transformation, Feature Scaling)"
          ],
          "learning_activities": [
            "Lecture: Introduction to ML concepts and types.",
            "Hands-on coding workshop: Data preprocessing using Python (pandas, numpy)."
          ],
          "readings_resources": [
            "Required: Chapter 1 of 'Introduction to Machine Learning with Python'",
            "Optional: Online articles on different types of Machine Learning."
          ],
          "assessments_milestones": [
            "Quiz 1: Basic ML concepts and data preprocessing (Due end of week)."
          ],
          "progressive_skill_building": [
            "Basic Python programming skills reinforced.",
            "Introduction to data manipulation and cleaning techniques."
          ]
        },
        "Week_2": {
          "topics": [
            "Introduction to Classification",
            "Logistic Regression",
            "K-Nearest Neighbors (KNN)"
          ],
          "learning_activities": [
            "Lecture: Introduction to Classification algorithms.",
            "Hands-on coding workshop: Implementing Logistic Regression using scikit-learn."
          ],
          "readings_resources": [
            "Required: Chapter 2 of 'Introduction to Machine Learning with Python'"
          ],
          "assessments_milestones": [
            "Quiz 2: Classification concepts and algorithms (Due end of week)."
          ],
          "progressive_skill_building": [
            "Understanding of different classification algorithms.",
            "Implementation of Logistic Regression and KNN."
          ]
        }
      }
    }
  }
};

// Simulate frontend data extraction
const syllabusData = sampleResponse.result;
const syllabus = syllabusData.syllabus || {};
const weeklySchedule = syllabus.weekly_schedule || {};
const actualWeeklySchedule = weeklySchedule || {};

console.log("=== Frontend Data Extraction Test ===");
console.log("Syllabus Data:", !!syllabusData);
console.log("Syllabus:", !!syllabus);
console.log("Weekly Schedule:", !!weeklySchedule);
console.log("Actual Weekly Schedule:", !!actualWeeklySchedule);
console.log("Weekly Schedule Keys:", Object.keys(actualWeeklySchedule));
console.log("Number of weeks:", Object.keys(actualWeeklySchedule).length);

if (Object.keys(actualWeeklySchedule).length > 0) {
  console.log("\n✅ Should show weekly schedule");
  Object.entries(actualWeeklySchedule).forEach(([weekKey, weekData]) => {
    console.log(`- ${weekKey}: ${weekData.topics?.length || 0} topics`);
  });
} else {
  console.log("\n❌ Would show 'No Weekly Schedule Available'");
}

console.log("\n=== Sample Week Data ===");
const firstWeek = Object.entries(actualWeeklySchedule)[0];
if (firstWeek) {
  const [weekKey, weekData] = firstWeek;
  console.log(`Week: ${weekKey}`);
  console.log(`Topics: ${weekData.topics?.length || 0}`);
  console.log(`Activities: ${weekData.learning_activities?.length || 0}`);
  console.log(`Resources: ${weekData.readings_resources?.length || 0}`);
  console.log(`Assessments: ${weekData.assessments_milestones?.length || 0}`);
  console.log(`Skills: ${weekData.progressive_skill_building?.length || 0}`);
}
