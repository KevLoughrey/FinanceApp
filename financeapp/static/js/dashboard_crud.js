document.addEventListener('DOMContentLoaded', () => {
    function toggleEditForm(type, id, showEdit) {
        const row = document.getElementById(`${type}-row-${id}`);
        const form = document.getElementById(`${type}-edit-${id}`);
        if (row && form) {
            if (showEdit) {
                row.classList.add('d-none');
                form.classList.remove('d-none');
            } else {
                form.classList.add('d-none');
                row.classList.remove('d-none');
            }
        }
    }

    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            const type = btn.dataset.type;
            toggleEditForm(type, id, true);
        });
    });

    document.querySelectorAll('.cancel-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.dataset.id;
            const type = btn.dataset.type;
            toggleEditForm(type, id, false);
        });
    });

    document.querySelectorAll('.expense-edit-form, .income-edit-form').forEach(form => {
        form.addEventListener('submit', e => {
            e.preventDefault();
            const id = form.dataset.id;
            const type = form.dataset.type;

            form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            data.amount = parseFloat(data.amount);

            fetch(`/finances/edit_${type}/${id}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data),
                })
                .then(res => res.json())
                .then(response => {
                    if (response.success) {
                        const r = response[type];
                        const row = document.getElementById(`${type}-row-${id}`);
                        row.querySelector('.date').textContent = r.date;
                        row.querySelector('.name').textContent = r.name;
                        row.querySelector('.amount').textContent = `€${Number.parseFloat(r.amount).toFixed(2)}`;
                        row.querySelector('.category').textContent = r.category_name;
                        row.querySelector('.description').textContent = r.description || '-';

                        toggleEditForm(type, id, false);
                    } else if (response.errors) {
                        for (const [field, messages] of Object.entries(response.errors)) {
                            const input = form.querySelector(`[name="${field}"]`);
                            if (input) input.classList.add('is-invalid');
                        }
                    }
                });
        });
    });

    let itemIdToDelete = null;
    let itemTypeToDelete = null;

    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            itemIdToDelete = btn.dataset.id;
            itemTypeToDelete = btn.dataset.type;

            const modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
            modal.show();
        });
    });

    document.getElementById('confirmDeleteBtn').addEventListener('click', () => {
        if (!itemIdToDelete || !itemTypeToDelete) return;

        fetch(`/finances/delete_${itemTypeToDelete}/${itemIdToDelete}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => {
                if (response.ok) {
                    document.getElementById(`${itemTypeToDelete}-row-${itemIdToDelete}`)?.remove();
                    document.getElementById(`${itemTypeToDelete}-edit-${itemIdToDelete}`)?.remove();
                } else {
                    alert(`Failed to delete ${itemTypeToDelete}.`);
                }
                bootstrap.Modal.getInstance(document.getElementById('deleteConfirmModal')).hide();
                itemIdToDelete = null;
                itemTypeToDelete = null;
            });
    });
});