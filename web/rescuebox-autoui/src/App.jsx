// React imports
import { useState, useEffect } from 'react';
import '@mantine/core/styles.css';
import { MantineProvider, Box, Stack, Text, Anchor, Grid, Button, Textarea, Input, Checkbox } from '@mantine/core';
import { useForm } from '@mantine/form';

// Import CSS
import './App.css';

// Recursive component to render each group and command
const TreeNode = ({ node, level = 0, onCommandClick }) => {
  return (
    <Box pl={level * 16} className={level > 0 ? "tree-indent" : ""}>
      {node.is_group ? (
        <>
          <Text className="tree-group" mt={4} mb={4}>{node.name}</Text>
          <Stack spacing={0} gap="xs">
            {node.children.map((child, index) => (
              <TreeNode key={index} node={child} level={level + 1} onCommandClick={onCommandClick} />
            ))}
          </Stack>
        </>
      ) : (
        <Anchor href="#" className="tree-command" onClick={() => onCommandClick(node)}>
          <Text mt={2} mb={2}>{node.name}</Text>
        </Anchor>
      )}
    </Box>
  );
};

const TreeView = ({ tree, onCommandClick }) => {
  return (
    <Box className="tree-view-container">
      <TreeNode node={tree} onCommandClick={onCommandClick} />
    </Box>
  );
};

// Main component
const App = () => {
  const [tree, setTree] = useState({});
  const [selectedCommand, setSelectedCommand] = useState(null);
  const [commandOutput, setCommandOutput] = useState('');

  useEffect(() => {
    // Retrieve JSON data from the script tag
    setTree(JSON.parse(document.getElementById("tree").textContent));
  }, []);

  const handleCommandClick = (command) => {
    setSelectedCommand(command);
    setCommandOutput(''); // Clear output when selecting a new command
  };

  // Initialize form with dynamic initial values based on the selected command
  const form = useForm({
    initialValues: selectedCommand
      ? selectedCommand.inputs.reduce((values, input) => {
          values[input.name] = input.default || '';
          return values;
        }, {})
      : {},
  });

  const handleRunCommand = () => {
    // Simulate command execution with form values
    setCommandOutput(`Executing ${selectedCommand.name} with parameters ${JSON.stringify(form.values)}...\nOutput: Command executed successfully!`);
  };

  return (
    <MantineProvider>
      <Grid grow>
        {/* Left Panel: Command Tree */}
        <Grid.Col span={4} className="grid-column">
          <Text size="xl" weight={700} mt={0} mb={12} className="tree-view-title">
            Rescuebox CLI
          </Text>
          <TreeView tree={tree} onCommandClick={handleCommandClick} />
        </Grid.Col>

        {/* Right Panel: Command Details and Output */}
        <Grid.Col span={8} className="grid-column">
          {selectedCommand ? (
            <>
              <Text size="xl" weight={600} mb={8}>{selectedCommand.name}</Text>
              <Text mb={12} color="dimmed">{selectedCommand.help || 'No description available.'}</Text>

              {/* Command Form */}
              <form onSubmit={form.onSubmit(handleRunCommand)} className="command-form">
                <Stack spacing="xs" mb={12}>
                  {selectedCommand.inputs.map((input) => (
                    <Box key={input.name}>
                      {input.help && <Text size="sm" color="dimmed" mb={4}>{input.help}</Text>}
                      {input.type === 'str' && (
                        <Input
                          placeholder={input.default || ''}
                          {...form.getInputProps(input.name)}
                          required
                        />
                      )}
                      {input.type === 'int' && (
                        <Input
                          type="number"
                          placeholder={input.default?.toString() || ''}
                          {...form.getInputProps(input.name)}
                          required
                        />
                      )}
                      {input.type === 'bool' && (
                        <Checkbox
                          label={input.name}
                          {...form.getInputProps(input.name, { type: 'checkbox' })}
                        />
                      )}
                    </Box>
                  ))}
                  <Button type="submit">Run Command</Button>
                </Stack>
              </form>

              {/* Command Output */}
              <Text mt={16} mb={4} weight={500}>Command Output:</Text>
              <Textarea value={commandOutput} readOnly minRows={6} className="command-output" />
            </>
          ) : (
            <Text>Select a command from the left panel to see details</Text>
          )}
        </Grid.Col>
      </Grid>
    </MantineProvider>
  );
};

export default App;
