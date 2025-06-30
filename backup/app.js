async function loadTasks() {
    const group = document.getElementById('groupFilter').value;
    const completed = document.getElementById('completedFilter').value;
    let url = 'http://127.0.0.1:8000/tasks?limit=20';
    if (group) url += `&group=${encodeURIComponent(group)}`;
    if (completed) url += `&completed=${completed}`;
    const res = await fetch(url);
    const data = await res.json();
    const ul = document.getElementById('tasks');
    ul.innerHTML = '';
    data.forEach(task => {
        const li = document.createElement('li');
        li.textContent = `[${task.group}] ${task.description} (User: ${task.user_id}) - ${task.completed ? '✅' : '❌'}`;
        ul.appendChild(li);
    });
}
window.loadTasks = loadTasks;
window.onload = loadTasks;

document.getElementById('addTaskForm').onsubmit = async function(e) {
    e.preventDefault();
    const user_id = parseInt(document.getElementById('userIdInput').value, 10);
    const group = document.getElementById('groupInput').value;
    const description = document.getElementById('descInput').value;
    const completed = document.getElementById('completedInput').checked;
    const task = { user_id, group, description, completed };
    await fetch('http://127.0.0.1:8000/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(task)
    });
    loadTasks();
    e.target.reset();
};