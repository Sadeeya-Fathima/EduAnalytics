(function () {
  const data = window.analyticsData || {};
  const palette = ['#4f46e5', '#0f766e', '#d97706', '#c2410c', '#7c3aed'];
  const layout = { autosize: true, margin: { t: 24, r: 24, b: 64, l: 56 }, font: { family: 'Inter, Arial, sans-serif', color: '#344054', size: 12 }, paper_bgcolor: 'transparent', plot_bgcolor: 'transparent', hovermode: 'closest', bargap: 0.34, barcornerradius: 8, hoverlabel: { bgcolor: '#172b4d', bordercolor: '#172b4d', font: { color: '#ffffff', size: 13, family: 'Inter, Arial, sans-serif' }, align: 'left' }, xaxis: { automargin: true, tickfont: { color: '#667085' }, titlefont: { color: '#475467', size: 12 }, gridcolor: 'rgba(16,24,40,0)' }, yaxis: { automargin: true, tickfont: { color: '#667085' }, titlefont: { color: '#475467', size: 12 }, gridcolor: '#edf0f5', zerolinecolor: '#d0d5dd' } };
  const config = { responsive: true, displayModeBar: false };
  function convertToSelect(id, options, blankLabel) {
    const input = document.getElementById(id);
    if (!input || !options || !options.length) return;
    const select = document.createElement('select');
    select.id = input.id;
    select.name = input.name;
    select.className = input.className;
    select.innerHTML = '<option value="">' + blankLabel + '</option>' + options.map(option => '<option value="' + option + '">' + option + '</option>').join('');
    if (input.value !== '') {
      const matchingOption = Array.from(select.options).find(option => Number(option.value) === Number(input.value));
      if (matchingOption) select.value = matchingOption.value;
    }
    input.replaceWith(select);
  }
  function setupAssessmentSelector() {
    const form = document.querySelector('.filter-form');
    const academicFieldset = form && Array.from(form.querySelectorAll('fieldset')).find(fieldset => fieldset.querySelector('legend')?.textContent.trim() === 'Academic Performance');
    if (!form || !academicFieldset || !(data.assessmentOptions || []).length) return;
    academicFieldset.classList.add('academic-filter-fieldset');
    const filterEyebrow = document.querySelector('.filter-panel .dashboard-eyebrow');
    if (filterEyebrow) filterEyebrow.textContent = 'Filter & Explore';
    const selector = document.createElement('div');
    selector.className = 'assessment-selector filter-field';
    selector.innerHTML = '<label for="assessment_filter">Choose assessment to filter</label><select id="assessment_filter">' + data.assessmentOptions.map(item => '<option value="' + item.field + '">' + item.label + '</option>').join('') + '</select><small>Select one assessment, then choose its minimum and maximum.</small>';
    academicFieldset.insertBefore(selector, academicFieldset.children[1]);
    selector.querySelector('select').value = data.selectedAssessment || 'g3';
    const fields = {};
    data.assessmentOptions.forEach(item => { fields[item.field] = [document.getElementById(item.field + '_min'), document.getElementById(item.field + '_max')].map(input => input && input.closest('.filter-field')); });
    function updateAssessmentFields() {
      const selected = selector.querySelector('select').value;
      Object.entries(fields).forEach(([field, fieldElements]) => fieldElements.forEach(element => {
        if (element) element.hidden = field !== selected;
      }));
    }
    selector.querySelector('select').addEventListener('change', updateAssessmentFields);
    updateAssessmentFields();
  }
  function setupCheckboxFilter(selectId) {
    const select = document.getElementById(selectId);
    if (!select || !select.multiple) return;
    const wrapper = document.createElement('div');
    wrapper.className = 'filter-checkboxes';
    const hasSelection = Array.from(select.options).some(option => option.selected);
    Array.from(select.options).forEach(option => {
      const label = document.createElement('label');
      label.className = 'filter-checkbox';
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.name = select.name;
      checkbox.value = option.value;
      checkbox.checked = hasSelection ? option.selected : true;
      label.append(checkbox, document.createTextNode(option.textContent));
      wrapper.appendChild(label);
    });
    select.hidden = true;
    select.parentElement.appendChild(wrapper);
  }
  function setupFilterValidation() {
    const form = document.querySelector('.filter-form');
    if (!form) return;
    const error = document.createElement('p');
    error.className = 'filter-validation-error';
    error.setAttribute('role', 'alert');
    error.hidden = true;
    form.prepend(error);
    form.addEventListener('submit', event => {
      const problems = [];
      ['g1', 'g2', 'g3', 'studytime'].forEach(field => {
        const minimum = document.getElementById(field + '_min');
        const maximum = document.getElementById(field + '_max');
        if (minimum && maximum && minimum.value !== '' && maximum.value !== '' && Number(minimum.value) > Number(maximum.value)) {
          problems.push(`${field.toUpperCase()} minimum cannot be greater than maximum.`);
        }
      });
      if (problems.length) {
        event.preventDefault();
        error.textContent = problems.join(' ');
        error.hidden = false;
        error.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        error.hidden = true;
      }
    });
  }
  function setupRangeConstraints() {
    ['g1', 'g2', 'g3', 'studytime'].forEach(field => {
      const minimum = document.getElementById(field + '_min');
      const maximum = document.getElementById(field + '_max');
      if (!minimum || !maximum) return;
      function sync() {
        const minValue = minimum.value === '' ? null : Number(minimum.value);
        const maxValue = maximum.value === '' ? null : Number(maximum.value);
        Array.from(maximum.options || []).forEach(option => {
          option.disabled = minValue !== null && option.value !== '' && Number(option.value) < minValue;
        });
        Array.from(minimum.options || []).forEach(option => {
          option.disabled = maxValue !== null && option.value !== '' && Number(option.value) > maxValue;
        });
        if (minValue !== null && maxValue !== null && minValue > maxValue) {
          maximum.value = '';
          minimum.value = '';
        }
      }
      minimum.addEventListener('change', sync);
      maximum.addEventListener('change', sync);
      sync();
    });
  }
  function alignFilterSections() {
    document.querySelectorAll('.filter-form fieldset').forEach(fieldset => {
      const legend = fieldset.querySelector('legend');
      if (legend && legend.textContent.trim() === 'Attendance') fieldset.classList.add('attendance-fieldset');
    });
  }
  function setupFilterDisclosure() {
    const panel = document.querySelector('.filter-panel');
    const form = panel && panel.querySelector('.filter-form');
    const heading = panel && panel.querySelector('.section-heading');
    if (!panel || !form || !heading) return;
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'filter-toggle';
    toggle.setAttribute('aria-expanded', 'false');
    const active = Object.keys(data.activeFilters || {}).length > 0;
    function setExpanded(expanded) {
      form.classList.toggle('is-collapsed', !expanded);
      toggle.textContent = expanded ? 'Hide Filters' : 'Show Filters';
      toggle.setAttribute('aria-expanded', String(expanded));
    }
    toggle.addEventListener('click', () => setExpanded(form.classList.contains('is-collapsed')));
    heading.appendChild(toggle);
    setExpanded(active);
  }
  (data.gradeOptions || []).length && ['g3_min', 'g3_max', 'g1_min', 'g1_max', 'g2_min', 'g2_max'].forEach(id => convertToSelect(id, data.gradeOptions, id.endsWith('_min') ? 'No minimum' : 'No maximum'));
  (data.studytimeNumericOptions || []).length && ['studytime_min', 'studytime_max'].forEach(id => convertToSelect(id, data.studytimeNumericOptions, id.endsWith('_min') ? 'No minimum' : 'No maximum'));
  setupAssessmentSelector();
  const absenceSelect = document.getElementById('absence_group');
  if (absenceSelect && absenceSelect.multiple) {
    absenceSelect.size = 1;
    const absenceHelper = absenceSelect.parentElement.querySelector('small');
    if (absenceHelper) absenceHelper.remove();
  }
  setupRangeConstraints();
  alignFilterSections();
  setupFilterDisclosure();
  setupFilterValidation();
  const filterSummary = document.querySelector('.filter-summary');
  if (filterSummary && Object.keys(data.activeFilters || {}).length) {
    const assessmentLabels = Object.fromEntries((data.assessmentOptions || []).map(item => [item.field, item.label]));
    const labels = { g1_min: `${assessmentLabels.g1 || 'G1'} minimum`, g1_max: `${assessmentLabels.g1 || 'G1'} maximum`, g2_min: `${assessmentLabels.g2 || 'G2'} minimum`, g2_max: `${assessmentLabels.g2 || 'G2'} maximum`, g3_min: `${assessmentLabels.g3 || data.finalAssessmentLabel || 'G3'} minimum`, g3_max: `${assessmentLabels.g3 || data.finalAssessmentLabel || 'G3'} maximum`, studytime_min: 'Minimum study hours', studytime_max: 'Maximum study hours', absence_group: 'Absence categories' };
    const summary = Object.entries(data.activeFilters).map(([key, value]) => `${labels[key] || key} : ${Array.isArray(value) ? value.join(', ') : value}`).join(' · ');
    filterSummary.innerHTML = '<b>Active filters:</b> ' + summary;
  }
  function chart(id, traces, extraLayout) {
    const el = document.getElementById(id);
    if (!el) return;
    if (!window.Plotly) {
      el.innerHTML = '<p class="chart-fallback">Chart unavailable while the visualization library is loading.</p>';
      return;
    }
    Plotly.newPlot(el, traces, Object.assign({}, layout, extraLayout || {}), config);
  }
  const distribution = data.distribution || [];
  const gradeLabels = distribution.map(x => `${x.label}<br>${x.lower}–${x.include_upper ? x.upper : '<' + x.upper}`);
  const gradeRanges = distribution.map(x => `${x.lower}–${x.include_upper ? x.upper : '<' + x.upper}`);
  chart('grade-distribution', [{ x: gradeLabels, y: distribution.map(x => x.count), customdata: distribution.map((x, index) => [gradeRanges[index], x.percentage]), type: 'bar', marker: { color: palette.slice(0, 5), line: { color: '#ffffff', width: 1 } }, hovertemplate: '<b>%{customdata[0]}</b><br>%{y} students<br>%{customdata[1]:.1f}% of valid grades<extra></extra>' }], { yaxis: { title: 'Number of students', rangemode: 'tozero' }, xaxis: { title: 'Performance category and grade range', tickangle: 0, automargin: true } });
  chart('assessment-comparison', [{ x: (data.assessments || []).map(x => x.label || x.field.toUpperCase()), y: (data.assessments || []).map(x => x.mean), type: 'bar', marker: { color: ['#4f46e5', '#0f766e', '#d97706'], line: { color: '#ffffff', width: 1 } }, hovertemplate: '<b>%{x}</b><br>Average: %{y:.2f}<extra></extra>' }], { yaxis: { title: 'Average grade', rangemode: 'tozero' }, xaxis: { title: 'Assessment' } });
  function groupChart(id, groups) {
    const items = groups || [];
    const total = items.reduce((sum, item) => sum + (item.count || 0), 0);
    const customdata = items.map(item => [item.count || 0, total ? ((item.count || 0) / total * 100) : 0]);
    const displayLabels = items.map(item => item.label
      .replace(' hours/week', ' h/wk')
      .replace('Above ', '>')
      .replace('No absences (0 days)', 'No absences')
      .replace('more than 10 days', '>10 days'));
    chart(id, [{ x: displayLabels, y: items.map(x => x.average_g3), customdata: items.map((item, index) => [item.label, customdata[index][0], customdata[index][1]]), type: 'bar', marker: { color: palette.slice(0, items.length), line: { color: '#ffffff', width: 1 } }, hovertemplate: '<b>%{customdata[0]}</b><br>Average ' + (data.finalAssessmentLabel || 'final grade') + ': %{y:.2f}<br>Students: %{customdata[1]}<br>%{customdata[2]:.1f}% of valid grades<extra></extra>' }], { yaxis: { title: 'Average ' + (data.finalAssessmentLabel || 'final grade'), rangemode: 'tozero' }, xaxis: { title: 'Group', automargin: true, tickangle: -18, tickfont: { size: 11 } }, margin: { l: 56, r: 24, t: 24, b: 82 } });
  }
  function scatterChart(id, points, xLabel, pointColor) {
    if (!points || !points.length) return;
    chart(id, [{ x: points.map(point => point.assessment), y: points.map(point => point.g3), mode: 'markers', type: 'scatter', marker: { color: pointColor, size: 9, opacity: 0.82, line: { color: '#ffffff', width: 1.5 } }, hovertemplate: '<b>' + xLabel + ': %{x:.2f}</b><br>' + (data.finalAssessmentLabel || 'Final grade') + ': %{y:.2f}<extra></extra>' }], { xaxis: { title: xLabel, rangemode: 'tozero' }, yaxis: { title: data.finalAssessmentLabel || 'Final grade', rangemode: 'tozero' } });
  }
  if (data.studytime && data.studytime.available) groupChart('studytime-analysis', data.studytime.groups);
  if (data.absences && data.absences.available) groupChart('absence-analysis', data.absences.groups);
  scatterChart('g1-g3-scatter', data.assessmentScatter && data.assessmentScatter.g1, (data.assessments || []).find(item => item.field === 'g1')?.label || 'G1', '#0f766e');
  scatterChart('g2-g3-scatter', data.assessmentScatter && data.assessmentScatter.g2, (data.assessments || []).find(item => item.field === 'g2')?.label || 'G2', '#d97706');
}());
