import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [tasks, setTasks] = useState([]);
  const [desc, setDesc] = useState("");
  const [userId, setUserId] = useState("");
  const [formCategory, setFormCategory] = useState("");
  const [formCompleted, setFormCompleted] = useState(false);
  const [formPercent, setFormPercent] = useState(0);
  const [category, setCategory] = useState("");
  const [completed, setCompleted] = useState(null);
  const [night, setNight] = useState(false);
  const [notification, setNotification] = useState("");
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedTasks, setSelectedTasks] = useState([]);
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("asc");

  useEffect(() => {
    document.body.className = night ? "night-mode" : "light-mode";
  }, [night]);

  const loadTasks = async () => {
    // Use URLSearchParams for a cleaner and safer way to build the URL
    const params = new URLSearchParams({
      sort_by: sortBy,
      order: sortOrder,
    });

    if (category.trim()) {
      params.append("category", category.trim());
    }
    if (completed !== null) {
      params.append("completed", completed);
    }

    try {
      // Corrected: Use the single, powerful /tasks endpoint
      const response = await fetch(`http://127.0.0.1:8000/tasks?${params.toString()}`);
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
  }, [completed, category, sortBy, sortOrder]);

  const showNotification = (message) => {
    setNotification(message);
    setTimeout(() => {
      setNotification("");
    }, 3000);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!desc.trim() || !userId.trim() || !formCategory.trim()) {
      showNotification("All fields are required.");
      return;
    }

    const newTask = {
      user_id: parseInt(userId, 10),
      category: formCategory.trim(),
      description: desc.trim(),
      completed: formCompleted,
      percent_complete: formCompleted ? 100 : parseFloat(formPercent),
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
      loadTasks();
      setDesc("");
      setFormCategory("");
      setUserId("");
      setFormCompleted(false);
      setFormPercent(0);
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
      await Promise.all(
        selectedTasks.map((taskId) =>
          fetch(`http://127.0.0.1:8000/tasks/${taskId}`, {
            method: "DELETE",
          })
        )
      );
      showNotification("Selected tasks deleted successfully.");
      loadTasks();
      setSelectedTasks([]);
      setSelectionMode(false);
    } catch (error) {
      console.error("Error deleting tasks:", error);
      showNotification("Error deleting tasks.");
    }
  };

  const handleToggleComplete = async (task) => {
    const updatedData = { completed: !task.completed };

    try {
      const response = await fetch(`http://127.0.0.1:8000/tasks/${task.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedData),
      });

      if (!response.ok) {
        throw new Error("Failed to update task status");
      }

      showNotification("Task status updated!");
      loadTasks();
    } catch (error) {
      console.error("Error updating task:", error);
      showNotification("Error updating task.");
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
          setSelectedTasks([]);
        }}
      >
        {selectionMode ? "Cancel Selection" : "Select Tasks to Delete"}
      </button>

      <div className="controls-container">
        <div className="filter-controls">
          <label>
            Filter Category:{" "}
            <input
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="Enter Category"
            />
          </label>
          <label>
            Filter Status:{" "}
            <select
              value={completed === null ? "" : String(completed)}
              onChange={(e) => {
                const value = e.target.value;
                if (value === "") {
                  setCompleted(null);
                } else {
                  setCompleted(value === "true");
                }
              }}
            >
              <option value="">Any</option>
              <option value="true">Completed</option>
              <option value="false">Not Completed</option>
            </select>
          </label>
        </div>
        
        <div className="sort-controls">
          <label>
            Sort By:{" "}
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="created_at">Date Created</option>
              <option value="updated_at">Date Updated</option>
            </select>
          </label>
          <label>
            Order:{" "}
            <select value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
              <option value="asc">Ascending</option>
              <option value="desc">Descending</option>
            </select>
          </label>
        </div>
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
          value={formCategory}
          onChange={(e) => setFormCategory(e.target.value)}
          placeholder="Category"
          required
        />
        <input
          type="text"
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
          placeholder="Description"
          required
        />
        <input
          type="number"
          value={formPercent}
          onChange={(e) => setFormPercent(e.target.value)}
          placeholder="%"
          min="0"
          max="100"
          disabled={formCompleted}
          style={{ width: "80px" }}
        />
        <label>
          Completed:
          <input
            type="checkbox"
            checked={formCompleted}
            onChange={(e) => {
              const isChecked = e.target.checked;
              setFormCompleted(isChecked);
              if (isChecked) {
                setFormPercent(100);
              }
            }}
          />
        </label>
        <button type="submit">Add Task</button>
      </form>
      {notification && <div className="notification">{notification}</div>}
      {selectionMode && selectedTasks.length > 0 && (
        <button
          onClick={handleDeleteSelected}
          style={{ margin: "1rem 0", background: "var(--danger)" }}
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
              [{task.category}] {task.description} ({(task.percent_complete ?? 0).toFixed(1)}%) -{" "}
              <span
                className="task-status"
                onClick={(e) => {
                  e.stopPropagation();
                  handleToggleComplete(task);
                }}
              >
                {task.completed ? "✅" : "❌"}
              </span>
              <br />
              <small>
                Added:{" "}
                {task.created_at
                  ? new Date(task.created_at).toLocaleString()
                  : "N/A"}
                {task.updated_at && (
                  <>
                    {" "}
                    | Updated:{" "}
                    {new Date(task.updated_at).toLocaleString()}
                  </>
                )}
                {task.completed_at && (
                  <>
                    {" "}
                    | Completed:{" "}
                    {new Date(task.completed_at).toLocaleString()}
                  </>
                )}
              </small>
            </span>
            {selectionMode && (
              <span
                className="selection-box"
                onClick={(e) => {
                  e.stopPropagation();
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