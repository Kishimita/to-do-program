import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [tasks, setTasks] = useState([]);
  const [desc, setDesc] = useState("");
  const [userId, setUserId] = useState("");
  const [formGroup, setFormGroup] = useState("");
  const [formCompleted, setFormCompleted] = useState(false);
  const [group, setGroup] = useState("");
  const [completed, setCompleted] = useState("");
  const [night, setNight] = useState(false);
  const [notification, setNotification] = useState("");
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedTasks, setSelectedTasks] = useState([]);

  useEffect(() => {
    document.body.className = night ? "night-mode" : "light-mode";
  }, [night]);

  const loadTasks = async () => {
    let url = `http://127.0.0.1:8000/tasks?limit=100`;
    if (group) url += `&group=${group}`;
    if (completed !== "") url += `&completed=${completed}`;
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setTasks(data);
    } catch (error) {
      console.error("Failed to load tasks:", error);
      showNotification("Failed to load tasks.");
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const showNotification = (message) => {
    setNotification(message);
    setTimeout(() => {
      setNotification("");
    }, 3000);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!desc.trim() || !userId.trim() || !formGroup.trim()) {
      showNotification("All fields are required.");
      return;
    }

    const newTask = {
      user_id: parseInt(userId, 10),
      group: formGroup,
      description: desc,
      completed: formCompleted,
    };

    try {
      const response = await fetch("http://127.0.0.1:8000/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newTask),
      });
      if (!response.ok) {
        throw new Error("Failed to add task");
      }
      await response.json();
      showNotification("Task added successfully!");
      loadTasks(); // Reload tasks to show the new one
      setDesc("");
      setFormGroup("");
      setUserId("");
      setFormCompleted(false);
    } catch (error) {
      console.error("Error adding task:", error);
      showNotification("Error adding task.");
    }
  };

  const toggleTaskSelection = (taskId) => {
    setSelectedTasks((prevSelected) =>
      prevSelected.includes(taskId)
        ? prevSelected.filter((id) => id !== taskId)
        : [...prevSelected, taskId]
    );
  };

  const handleDeleteSelected = async () => {
    if (selectedTasks.length === 0) {
      showNotification("No tasks selected to delete.");
      return;
    }
    try {
      // We need to find the user_id for each task to pass to the backend
      const tasksToDelete = selectedTasks.map((taskId) => {
        const task = tasks.find((t) => t.id === taskId);
        return fetch(
          `http://127.0.0.1:8000/tasks/${taskId}?user_id=${task.user_id}`,
          {
            method: "DELETE",
          }
        );
      });

      await Promise.all(tasksToDelete);

      showNotification("Selected tasks deleted successfully.");
      loadTasks(); // Refresh the list
      setSelectedTasks([]); // Clear selection
      setSelectionMode(false); // Exit selection mode
    } catch (error) {
      console.error("Error deleting tasks:", error);
      showNotification("Error deleting tasks.");
    }
  };

  return (
    <div className="App">
      <h1>To-Do List</h1>
      <button onClick={() => setNight((n) => !n)}>
        {night ? "☀️ Light Mode" : "🌙 Night Mode"}
      </button>
      <button
        style={{ marginLeft: "1rem" }}
        onClick={() => {
          setSelectionMode(!selectionMode);
          setSelectedTasks([]); // Clear selections when toggling mode
        }}
      >
        {selectionMode ? "Cancel Selection" : "Select Tasks to Delete"}
      </button>
      <div>
        <label>
          Group:{" "}
          <input
            value={group}
            onChange={(e) => setGroup(e.target.value)}
            placeholder="Filter by Group"
          />
        </label>
        <label>
          Status:{" "}
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
      {selectionMode && selectedTasks.length > 0 && (
        <button
          onClick={handleDeleteSelected}
          style={{ margin: "1rem 0", background: "#d9534f" }}
        >
          Delete Selected ({selectedTasks.length})
        </button>
      )}
      <ul id="tasks">
        {tasks.map((task) => (
          <li
            key={task.id}
            className={`task-item${
              selectedTasks.includes(task.id) ? " selected" : ""
            }`}
            onClick={() => {
              if (selectionMode) toggleTaskSelection(task.id);
            }}
          >
            <span>
              [{task.group}] {task.description} (User: {task.user_id}) -{" "}
              {task.completed ? "✅" : "❌"}
              <br />
              <small>
                Added:{" "}
                {task.created_at
                  ? new Date(task.created_at).toLocaleString()
                  : "N/A"}
                {task.completed_at && (
                  <>
                    {" "}
                    | Completed:{" "}
                    {new Date(task.completed_at).toLocaleString()}
                  </>
                )}
                {task.deleted_at && (
                  <>
                    {" "}
                    | Deleted: {new Date(task.deleted_at).toLocaleString()}
                  </>
                )}
              </small>
            </span>
            {selectionMode && (
              <span
                className="selection-box"
                onClick={(e) => {
                  e.stopPropagation(); // Prevent li's onClick from firing
                  toggleTaskSelection(task.id);
                }}
              >
                {selectedTasks.includes(task.id) ? "☑️" : "⬜️"}
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;