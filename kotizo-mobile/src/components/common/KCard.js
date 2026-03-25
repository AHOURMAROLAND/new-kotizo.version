import React from 'react';
import { View, StyleSheet } from 'react-native';
import useThemeStore from '../../store/themeStore';

export default function KCard({ children, style, secondary = false }) {
  const { colors } = useThemeStore();
  return (
    <View style={[
      styles.card,
      { backgroundColor: secondary ? colors.cardSecondary : colors.card, borderColor: colors.border },
      style,
    ]}>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
  },
});
