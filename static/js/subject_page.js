// JS extracted from subject.html for cleaner template.
(function(){
  // Tab handling
  function showTab(tab) {
    document.getElementById('panel-assignments').classList.toggle('hidden', tab !== 'assignments');
    document.getElementById('panel-summary').classList.toggle('hidden', tab !== 'summary');
    document.getElementById('tab-assignments').classList.toggle('tab-active', tab === 'assignments');
    document.getElementById('tab-summary').classList.toggle('tab-active', tab === 'summary');
  }
  window.showTab = showTab;

  // Subject edit form
  window.showSubjectEditForm = function() {
    document.getElementById('subject-edit-form').classList.remove('hidden');
    document.getElementById('subject-code-display').classList.add('hidden');
    document.getElementById('subject-name-display').classList.add('hidden');
    document.getElementById('edit-subject-btn').classList.add('hidden');
  };
  window.hideSubjectEditForm = function() {
    document.getElementById('subject-edit-form').classList.add('hidden');
    document.getElementById('subject-code-display').classList.remove('hidden');
    document.getElementById('subject-name-display').classList.remove('hidden');
    document.getElementById('edit-subject-btn').classList.remove('hidden');
  };
  window.submitSubjectEditForm = function(event) { return true; };

  // Inline edit state
  let editing_assignment_id = null;
  let original_row_html = null;
  window.startInlineEditAssignment = function(id) {
    if (editing_assignment_id !== null) { window.cancelInlineEditAssignment(); }
    editing_assignment_id = id;
    const row = document.querySelector(`tr[data-assignment-id='${id}']`);
    if (!row) return;
    original_row_html = row.innerHTML;
    fetch(`${window.subjectBasePath}/assignment/${id}/edit?year=${window.subjectYear}`)
      .then(r => r.text())
      .then(html => { row.innerHTML = html; });
  };
  window.cancelInlineEditAssignment = function() {
    if (editing_assignment_id !== null) {
      const row = document.querySelector(`tr[data-assignment-id='${editing_assignment_id}']`);
      if (row && original_row_html) row.innerHTML = original_row_html;
      editing_assignment_id = null; original_row_html = null;
    }
  };
  window.submitInlineEditAssignmentRow = function(id, year) {
    const row = document.querySelector(`tr[data-assignment-id='${id}']`);
    if (!row) return false;
    const assessment = row.querySelector("input[name='assessment']")?.value || '';
    const weighted_mark = row.querySelector("input[name='weighted_mark']")?.value || '';
    const mark_weight = row.querySelector("input[name='mark_weight']")?.value || '';
    const grade_type = row.querySelector("select[name='grade_type']")?.value || 'numeric';
    const formData = new FormData();
    formData.append('assessment', assessment);
    formData.append('weighted_mark', weighted_mark);
    formData.append('mark_weight', mark_weight);
    formData.append('grade_type', grade_type);
    formData.append('year', year);
    fetch(`${window.subjectBasePath}/assignment/${id}/update`, { method: 'POST', body: formData })
      .then(r => r.json())
      .then(data => {
        if (data.success && typeof data.row_html === 'string') {
          row.innerHTML = data.row_html;
          editing_assignment_id = null; original_row_html = null;
        } else {
          row.innerHTML = `<td colspan='6'><div class='alert alert-error mb-2'>${data.error || 'Unknown error.'}</div></td>`;
        }
      })
      .catch(() => { row.innerHTML = `<td colspan='6'><div class='alert alert-error mb-2'>Error submitting edit.</div></td>`; });
    return false;
  };

  window.updateQueryStringParameter = function(uri, key, value) {
    const re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
    const separator = uri.indexOf('?') !== -1 ? '&' : '?';
    if (value === '' || value === null) {
      return uri.replace(re, '$1').replace(/[?&]$/, '');
    }
    if (uri.match(re)) return uri.replace(re, '$1' + key + '=' + value + '$2');
    return uri + separator + key + '=' + value;
  };

  document.addEventListener('DOMContentLoaded', function() { showTab('assignments'); });
})();
