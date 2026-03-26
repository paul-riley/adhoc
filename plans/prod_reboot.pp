plan adhoc::prod_reboot (
  String $reboot_section,
) {
  $query = [
    'from', 'nodes',
    ['=', ['fact', 'reboot_section'], $reboot_section]
  ]
  $rows = puppetdb_query($query)
# Query PuppetDB for nodes in this reboot group

  $nodes = $rows.map |$row| { $row['certname'] }

  notice("Found ${nodes.length} nodes in reboot group ${reboot_section}")

  # Convert certnames into Bolt targets
  $targets = get_targets($nodes)

  # Run the reboot task
  $result = run_task('reboot', $targets)

  return $result
}
