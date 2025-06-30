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

      const formData = new FormData(form);
      const data = Object.fromEntries(formData.entries());
      data.amount = parseFloat(data.amount);

      fetch(`/finances/edit_expense/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      .then(response => response.json())
      .then(response => {
        if (response.success) {
          let rdata = response.expense;
          const row = document.getElementById(`expense-row-${id}`);
          row.querySelector('td.date').textContent = rdata.date;
          row.querySelector('td.name').textContent = rdata.name;
          row.querySelector('td.amount').textContent = `€${Number.parseFloat(rdata.amount).toFixed(2)}`;
          row.querySelector('td.category').textContent = rdata.category_name;
          row.querySelector('td.description').textContent = rdata.description;
          document.getElementById(`expense-edit-${id}`).classList.add('d-none');
          row.classList.remove('d-none');
        }
        // TODO: add else
      });
    });
  });
});
