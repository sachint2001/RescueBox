// React imports
import { useState, useEffect } from 'react';

// Mantine imports
import '@mantine/core/styles.css';
import { MantineProvider, Box, Stack, Text, Anchor, Divider } from '@mantine/core';

// Local styles
import './index.css';

// Recursive component to render each group and command
const TreeNode = ({ node, level = 0 }) => {
  return (
    <Box pl={level * 16} className={level > 0 ? "tree-indent" : ""}> {/* Indent based on level */}
      {node.is_group ? (
        <>
          <Text className="tree-group" mt={4} mb={4}>{node.name}</Text>
          <Stack spacing={0} gap="xs">
            {node.children.map((child, index) => (
              <TreeNode key={index} node={child} level={level + 1} />
            ))}
          </Stack>
        </>
      ) : (
        <Anchor href={node.endpoint} className="tree-command">
          <Text mt={2} mb={2}>{node.name}</Text>
        </Anchor>
      )}
    </Box>
  );
};

const TreeView = ({ tree }) => {
  return (
    <Box className="tree-view-container">
      <TreeNode node={tree} />
    </Box>
  );
};

// Main component
const App = () => {
  const [tree, setTree] = useState({});
  
  useEffect(() => {
    // Retrieve JSON data from the script tag
    setTree(JSON.parse(document.getElementById("tree").textContent));
  }, []);

  return (
    <MantineProvider>
      <Box className="tree-view-container">
        <Text size="xl" weight={700} mt={0} mb={12} className="tree-view-title">
          Rescuebox CLI
        </Text>
        <TreeView tree={tree} />
      </Box>
    </MantineProvider>
  );
};

export default App;
