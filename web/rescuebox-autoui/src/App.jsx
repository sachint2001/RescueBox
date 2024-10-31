// React imports
import { useState, useEffect } from 'react';
import '@mantine/core/styles.css';
import { MantineProvider, Box, Stack, Text, Anchor, Grid, Button, Textarea, Input, Checkbox, Group } from '@mantine/core';
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

  const handleRunCommand = async () => {
    if (!selectedCommand) return;

    const inputs = {...form.values, 'streaming': true}
  
    try {
      const response = await fetch(selectedCommand.endpoint + '?' + new URLSearchParams(inputs).toString(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: form.values,
      });
  
      // Check if the response has a readable stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let resultText = '';
      let doneReading = false;
  
      while (!doneReading) {
        // Read the next chunk from the stream
        const { value, done } = await reader.read();
        
        if (done) break;
  
        // Decode the current chunk of the stream
        const chunk = decoder.decode(value, { stream: true });
        
        // Try parsing the current result as JSON to handle success/failure logic
        try {
          const commandResult = JSON.parse(chunk);
          resultText = commandResult.stdout;
  
          if (commandResult.success) {
            // Append stdout to the output as it arrives
            setCommandOutput(commandResult.stdout);
          } else {
            // If success is false, stop streaming and show stdout + error
            setCommandOutput(`${commandResult.stdout}\nError: ${parsedResult.error}`);
            reader.cancel(); // Stop reading further chunks
            doneReading = true;
          }
        } catch (error) {
          // If JSON parsing fails, continue to accumulate the text until we have a valid JSON
          setCommandOutput(resultText);
        }
      }
    } catch (error) {
      setCommandOutput(`Failed to execute command. Please try again. ${error}`);
    }
  };

  const handleReset = () => {
    if (selectedCommand) {
      // Reset form to initial values based on selected command

      // TODO: reset does not clear the form values
      form.reset();
      setCommandOutput('');
    }
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
              <Group justify="space-between" mb={8}>
                <Text size="xl" weight={600}>{selectedCommand.name}</Text>
                <Button variant="light" onClick={handleReset}>Reset</Button>
              </Group>
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
              <Textarea value={commandOutput} readOnly minRows={10} className="command-output" />
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
