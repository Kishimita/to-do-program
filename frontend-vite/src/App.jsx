import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  // State for tasks and form fields
  const [tasks, setTasks] = useState([]);
  const [group, setGroup] = useState("");
  const [completed, setCompleted] = useState("");
  const [userId, setUserId] = useState("");
  const [desc, setDesc] = useState("");
  const [formGroup, setFormGroup] = useState("");
  const [formCompleted, setFormCompleted] = useState(false);
  const [notification, setNotification] = useState("");
  const [night, setNight] = useState(localStorage.getItem("night") === "true");

  // Fetch tasks from backend
  const loadTasks = async () => {
    let url = "http://127.0.0.1:8000/tasks?limit=20";
    if (group) url += `&group=${encodeURIComponent(group)}`;
    if (completed) url += `&completed=${completed}`;
    const res = await fetch(url);
    const data = await res.json();
    setTasks(data);
  };

  useEffect(() => {
    loadTasks();
    // eslint-disable-next-line
  }, [group, completed]);

  // Handle form submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    const task = {
      user_id: parseInt(userId, 10),
      group: formGroup,
      description: desc,
      completed: formCompleted,
    };
    const res = await fetch("http://127.0.0.1:8000/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(task),
    });
    if (res.ok) {
      setNotification("Task added!");
      setTimeout(() => setNotification(""), 2000);
      setUserId("");
      setFormGroup("");
      setDesc("");
      setFormCompleted(false);
      loadTasks();
    } else {
      setNotification("Error adding task.");
      setTimeout(() => setNotification(""), 2000);
    }
  };

  // Night mode toggle
  useEffect(() => {
    document.body.className = night ? "night" : "";
    localStorage.setItem("night", night);
  }, [night]);

  return (
    <div className="App">
      <h1>To-Do List</h1>
      <button onClick={() => setNight((n) => !n)}>
        {night ? "☀️ Light Mode" : "🌙 Night Mode"}
      </button>
      <div>
        <label>
          Group:{" "}
          <input
            value={group}
            onChange={(e) => setGroup(e.target.value)}
            placeholder="Group"
          />
        </label>
        <label>
          Completed:{" "}
          <select
            value={completed}
            onChange={(e) => setCompleted(e.target.value)}
          >
            <option value="">Any</option>
            <option value="true">Completed</option>
            <option value="false">Not Completed</option>
          </select>
        </label>
        <button onClick={loadTasks}>Filter</button>
      </div>
      <form onSubmit={handleSubmit}>
        <input
          type="number"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="User ID"
          required
        />
        <input
          type="text"
          value={formGroup}
          onChange={(e) => setFormGroup(e.target.value)}
          placeholder="Group"
          required
        />
        <input
          type="text"
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
          placeholder="Description"
          required
        />
        <label>
          Completed:
          <input
            type="checkbox"
            checked={formCompleted}
            onChange={(e) => setFormCompleted(e.target.checked)}
          />
        </label>
        <button type="submit">Add Task</button>
      </form>
      {notification && <div className="notification">{notification}</div>}
      <ul id="tasks">
        {tasks.map((task, i) => (
          <li key={i} className="task-item">
            <span>
              [{task.group}] {task.description} (User: {task.user_id}) -{" "}
              {task.completed ? "✅" : "❌"}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;