// React imports
import { useState, useEffect } from 'react';
import '@mantine/core/styles.css';
import { MantineProvider, Box, Stack, Text, Anchor, Grid, Button, Textarea, Input } from '@mantine/core';

// Import CSS
import './App.css';

// Recursive component to render each group and command
const TreeNode = ({ node, level = 0, onCommandClick }) => {
  return (
    <Box pl={level * 16} className={level > 0 ? "tree-indent" : ""}> {/* Indent based on level */}
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
    console.log(command)
    setSelectedCommand(command);
    setCommandOutput(''); // Clear output when selecting a new command
  };

  const handleRunCommand = () => {
    // Simulate command execution by updating command output
    setCommandOutput(`Executing ${selectedCommand.name}...\nOutput: Command executed successfully!`);
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

        <Grid.Col span={8} className="grid-column">
          {selectedCommand ? (
            <>
              <Text size="xl" weight={600} mb={8}>{selectedCommand.name}</Text>
              <Text mb={12} >{selectedCommand.help}</Text>

              {/* Command Form */}
              <Stack spacing="xs" mb={12} className="command-form">
                {/* Add inputs dynamically based on command properties if available */}
                <Input placeholder="Argument 1" label="Argument 1" required />
                <Input placeholder="Argument 2" label="Argument 2" />
                {/* Add more inputs as needed for command parameters */}
                <Button onClick={handleRunCommand}>Run Command</Button>
              </Stack>

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
