document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            document.getElementById(`expense-row-${id}`).classList.add('d-none');
            document.getElementById(`expense-edit-${id}`).classList.remove('d-none');
        });
    });

    document.querySelectorAll('.cancel-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            document.getElementById(`expense-edit-${id}`).classList.add('d-none');
            document.getElementById(`expense-row-${id}`).classList.remove('d-none');
        });
    });

    document.querySelectorAll('.expense-edit-form').forEach(form => {
        form.addEventListener('submit', e => {
            e.preventDefault();
            const id = form.dataset.id;

            form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            data.amount = parseFloat(data.amount);

            fetch(`/finances/edit_expense/${id}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data),
                })
            .then(res => res.json())
            .then(response => {
                if (response.success) {
                    const r = response.expense;
                    const row = document.getElementById(`expense-row-${id}`);
                    row.querySelector('.date').textContent = r.date;
                    row.querySelector('.name').textContent = r.name;
                    row.querySelector('.amount').textContent = `€${Number.parseFloat(r.amount).toFixed(2)}`;
                    row.querySelector('.category').textContent = r.category_name;
                    row.querySelector('.description').textContent = r.description;

                    form.classList.add('d-none');
                    row.classList.remove('d-none');
                } else if (response.errors) {
                    for (const [field, messages] of Object.entries(response.errors)) {
                        const input = form.querySelector(`[name="${field}"]`);
                        if (input) input.classList.add('is-invalid');
                    }
                }
            });
        });
    });
    let expenseIdToDelete = null;

    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            expenseIdToDelete = btn.dataset.id;
            const modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
            modal.show();
        });
    });

    document.getElementById('confirmDeleteBtn').addEventListener('click', () => {
        if (!expenseIdToDelete) return;

        fetch(`/finances/delete_expense/${expenseIdToDelete}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
        .then(response => {
            if (response.ok) {
                document.getElementById(`expense-row-${expenseIdToDelete}`)?.remove();
                document.getElementById(`expense-edit-${expenseIdToDelete}`)?.remove();
            } else {
                // TODO: Better error handling here...
                alert('Failed to delete expense.');
            }
            bootstrap.Modal.getInstance(document.getElementById('deleteConfirmModal')).hide();
            expenseIdToDelete = null;
        });
    });
});