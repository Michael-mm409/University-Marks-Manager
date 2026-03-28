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
  window.submitSubjectEditForm = function(event) {
    const form = document.getElementById('subject-edit-form');
    const oldSemester = form.querySelector('[name="old_semester"]').value;
    const oldSubjectCode = form.querySelector('[name="old_subject_code"]').value;
    form.action = `/semester/${encodeURIComponent(oldSemester)}/subject/${encodeURIComponent(oldSubjectCode)}/update`;
    return true;
  };

  function getEditingRow(assessment, code, semester, year) {
    const escAssessment = assessment.replace(/'/g, "\\'");
    return document.querySelector(`tr[data-assessment='${escAssessment}'][data-code='${code}'][data-semester='${semester}'][data-year='${year}']`);
  }

  // Inline edit state
  let editing_assignment_keys = null;
  let original_row_html = null;
  window.startInlineEditAssignment = function(assessment, code, semester, year) {
    if (editing_assignment_keys !== null) { window.cancelInlineEditAssignment(); }
    editing_assignment_keys = { assessment, code, semester, year };
    const row = getEditingRow(assessment, code, semester, year);
    if (!row) {
        console.error("Could not find row to edit for:", assessment);
        return;
    }
    original_row_html = row.innerHTML;
    const url = `/semester/${encodeURIComponent(semester)}/subject/${encodeURIComponent(code)}/assignment/${encodeURIComponent(assessment)}/${encodeURIComponent(year)}/edit`;
    fetch(url, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
      }
    })
      .then(r => r.text())
      .then(html => { row.innerHTML = html; });
  };
  window.cancelInlineEditAssignment = function() {
    if (editing_assignment_keys && typeof editing_assignment_keys === 'object') {
      const { assessment, code, semester, year } = editing_assignment_keys;
      const row = getEditingRow(assessment, code, semester, year);
      if (row && original_row_html) row.innerHTML = original_row_html;
      editing_assignment_keys = null; original_row_html = null;
    } else {
      editing_assignment_keys = null; original_row_html = null;
    }
  };
  window.submitInlineEditAssignmentRow = function(assessment, code, semester, year) {
    const row = getEditingRow(assessment, code, semester, year);
    if (!row) return false;
    const new_assessment = row.querySelector("input[name='new_assessment']")?.value || assessment;
    const weighted_mark = row.querySelector("input[name='weighted_mark']")?.value || '';
    const mark_weight = row.querySelector("input[name='mark_weight']")?.value || '';
    const grade_type = row.querySelector("select[name='grade_type']")?.value || 'numeric';
    const is_exam = row.querySelector("input[name='is_exam']")?.checked || false;
    console.log('Submitting assignment update:', {old: assessment, new: new_assessment, changed: new_assessment !== assessment});
    const formData = new FormData();
    formData.append('assessment', assessment);
    formData.append('new_assessment', new_assessment);
    formData.append('subject_code', code);
    formData.append('semester_name', semester);
    formData.append('year', year);
    formData.append('weighted_mark', weighted_mark);
    formData.append('mark_weight', mark_weight);
    formData.append('grade_type', grade_type);
    formData.append('is_exam', is_exam ? 'true' : 'false');
    const url = `/semester/${encodeURIComponent(semester)}/subject/${encodeURIComponent(code)}/assignment/${encodeURIComponent(assessment)}/${encodeURIComponent(year)}/update`;
    fetch(url, { method: 'POST', body: formData, headers: { 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json' } })
      .then(async r => {
        const ct = r.headers.get('content-type') || '';
        if (!r.ok) {
          const text = await r.text().catch(() => '');
          console.error('Assignment update failed', r.status, text);
          row.innerHTML = `<td colspan='6'><div class='alert alert-error mb-2'>Server error: ${r.status}</div></td>`;
          return null;
        }
        if (ct.includes('application/json')) {
          return r.json();
        }
        // Non-JSON response (likely HTML redirect to login) - show text for debugging
        const text = await r.text().catch(() => '');
        console.warn('Assignment update returned non-JSON response', ct, text.slice(0, 400));
        row.innerHTML = `<td colspan='6'><div class='alert alert-error mb-2'>Unexpected server response.</div></td>`;
        return null;
      })
      .then(data => {
        if (!data) return;
        if (data && data.success) {
          if (data.reload_url) {
            window.location.assign(data.reload_url);
            return;
          }
          if (typeof data.row_html === 'string') {
            row.innerHTML = data.row_html;
            editing_assignment_keys = null; original_row_html = null;
            return;
          }
        }
        row.innerHTML = `<td colspan='6'><div class='alert alert-error mb-2'>${(data && data.error) || 'Unknown error.'}</div></td>`;
      })
      .catch(err => { console.error(err); row.innerHTML = `<td colspan='6'><div class='alert alert-error mb-2'>Error submitting edit.</div></td>`; });
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
